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


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def _kind(publication_types: list[str] | None) -> CandidateKind:
    values = {value.lower() for value in publication_types or []}
    if "preprint" in values:
        return CandidateKind.preprint
    if values:
        return CandidateKind.paper
    return CandidateKind.unknown


def parse_semantic_scholar_papers(payload: dict, query: DiscoveryQuery) -> list[PaperCandidate]:
    papers = payload.get("data", [])
    candidates: list[PaperCandidate] = []
    for rank, paper in enumerate(papers, start=1):
        paper_id = paper.get("paperId")
        open_access_pdf = paper.get("openAccessPdf") or {}
        external_ids = []
        if paper_id:
            external_ids.append(ExternalPaperId(provider="semantic_scholar", value=str(paper_id)))
        for key, value in (paper.get("externalIds") or {}).items():
            if value:
                external_ids.append(ExternalPaperId(provider=key.lower(), value=str(value)))

        authors = []
        for author in paper.get("authors") or []:
            if author.get("name"):
                author_ids = []
                if author.get("authorId"):
                    author_ids.append(
                        ExternalPaperId(provider="semantic_scholar", value=str(author["authorId"]))
                    )
                authors.append(PaperAuthor(name=str(author["name"]), external_ids=author_ids))

        source_url = paper.get("url")
        candidates.append(
            PaperCandidate(
                title=str(paper.get("title") or "Untitled Semantic Scholar paper"),
                kind=_kind(paper.get("publicationTypes")),
                status=CandidateStatus.needs_manual_review,
                external_ids=external_ids,
                authors=authors,
                abstract=paper.get("abstract"),
                publication_date=_date(paper.get("publicationDate")),
                source_url=source_url,
                pdf_url=open_access_pdf.get("url"),
                landing_page_url=source_url,
                confidence=0.78,
                discovery_paths=[
                    DiscoveryPath(
                        provider=SourceProvider.semantic_scholar,
                        query=query.query,
                        source_candidate_uuid=query.source_candidate_uuid,
                        result_rank=rank,
                        url=source_url,
                    )
                ],
                raw_provider_data={
                    "provider": "semantic_scholar",
                    "paperId": paper_id,
                    "publicationTypes": paper.get("publicationTypes") or [],
                    "openAccessPdf": open_access_pdf,
                },
            )
        )

    return candidates


class SemanticScholarClient:
    def __init__(
        self,
        http_client: httpx.Client | None = None,
        base_url: str = "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
        max_results: int = 10,
        api_key: str | None = None,
    ) -> None:
        self.http_client = http_client or httpx.Client()
        self.base_url = base_url
        self.max_results = max_results
        self.api_key = api_key

    def search(self, query: DiscoveryQuery) -> list[PaperCandidate]:
        headers = {"x-api-key": self.api_key} if self.api_key else None
        params = {
            "query": query.query,
            "limit": self.max_results,
            "fields": "title,url,abstract,authors,externalIds,publicationTypes,publicationDate,openAccessPdf",
        }
        response = self.http_client.get(self.base_url, params=params, headers=headers)
        response.raise_for_status()
        return parse_semantic_scholar_papers(response.json(), query)
