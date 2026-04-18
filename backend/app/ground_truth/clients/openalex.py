from datetime import date

import httpx

from app.ground_truth.queries import DiscoveryQuery
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    DiscoveryPath,
    ExternalPaperId,
    PaperAuthor,
    PaperCandidate,
    SourceProvider,
)


def _abstract_from_inverted_index(value: dict[str, list[int]] | None) -> str | None:
    if not value:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in value.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def parse_openalex_works(payload: dict, query: DiscoveryQuery) -> list[PaperCandidate]:
    results = payload.get("results", [])
    candidates: list[PaperCandidate] = []
    for rank, work in enumerate(results, start=1):
        open_access = work.get("open_access") or {}
        primary_location = work.get("primary_location") or {}
        landing_page_url = primary_location.get("landing_page_url") or work.get("id")
        pdf_url = primary_location.get("pdf_url") or open_access.get("oa_url")
        work_type = str(work.get("type") or "").lower()
        kind = CandidateKind.preprint if work_type == "preprint" else CandidateKind.paper
        status = CandidateStatus.rejected if work.get("is_retracted") else CandidateStatus.needs_manual_review

        external_ids = []
        if work.get("id"):
            external_ids.append(ExternalPaperId(provider="openalex", value=str(work["id"])))
        if work.get("doi"):
            external_ids.append(ExternalPaperId(provider="doi", value=str(work["doi"])))

        authors = []
        for authorship in work.get("authorships") or []:
            author = authorship.get("author") or {}
            if author.get("display_name"):
                author_ids = []
                if author.get("id"):
                    author_ids.append(ExternalPaperId(provider="openalex", value=str(author["id"])))
                authors.append(PaperAuthor(name=str(author["display_name"]), external_ids=author_ids))

        candidates.append(
            PaperCandidate(
                title=str(work.get("title") or work.get("display_name") or "Untitled OpenAlex work"),
                kind=kind,
                status=status,
                external_ids=external_ids,
                authors=authors,
                abstract=_abstract_from_inverted_index(work.get("abstract_inverted_index")),
                publication_date=_date(work.get("publication_date")),
                source_url=landing_page_url,
                pdf_url=pdf_url,
                landing_page_url=landing_page_url,
                confidence=0.8,
                discovery_paths=[
                    DiscoveryPath(
                        provider=SourceProvider.openalex,
                        query=query.query,
                        source_candidate_uuid=query.source_candidate_uuid,
                        result_rank=rank,
                        url=landing_page_url,
                    )
                ],
                raw_provider_data={
                    "provider": "openalex",
                    "id": work.get("id"),
                    "type": work.get("type"),
                    "is_retracted": work.get("is_retracted", False),
                    "open_access": open_access,
                },
                rejected_reason="openalex_is_retracted" if work.get("is_retracted") else None,
            )
        )

    return candidates


class OpenAlexClient:
    def __init__(
        self,
        http_client: httpx.Client | None = None,
        base_url: str = "https://api.openalex.org/works",
        max_results: int = 10,
        mailto: str | None = None,
    ) -> None:
        self.http_client = http_client or httpx.Client()
        self.base_url = base_url
        self.max_results = max_results
        self.mailto = mailto

    def search(self, query: DiscoveryQuery) -> list[PaperCandidate]:
        params: dict[str, str | int] = {
            "search": query.query,
            "per-page": self.max_results,
            "select": "id,doi,title,type,publication_date,abstract_inverted_index,authorships,open_access,primary_location,is_retracted",
        }
        if self.mailto:
            params["mailto"] = self.mailto

        response = self.http_client.get(self.base_url, params=params)
        response.raise_for_status()
        return parse_openalex_works(response.json(), query)
