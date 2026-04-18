from datetime import date
from urllib.parse import urlparse
from xml.etree import ElementTree

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

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _text(entry: ElementTree.Element, path: str) -> str | None:
    element = entry.find(path, ATOM_NS)
    if element is None or element.text is None:
        return None
    return " ".join(element.text.split())


def _arxiv_id_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1]


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def parse_arxiv_atom(xml_text: str, query: DiscoveryQuery) -> list[PaperCandidate]:
    root = ElementTree.fromstring(xml_text)
    candidates: list[PaperCandidate] = []
    for rank, entry in enumerate(root.findall("atom:entry", ATOM_NS), start=1):
        title = _text(entry, "atom:title") or "Untitled arXiv paper"
        abstract_url = _text(entry, "atom:id")
        arxiv_id = _arxiv_id_from_url(abstract_url or "")
        pdf_url = None
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href")
                break

        authors = [
            PaperAuthor(name=name)
            for author in entry.findall("atom:author", ATOM_NS)
            if (name := _text(author, "atom:name"))
        ]
        external_ids = [ExternalPaperId(provider="arxiv", value=arxiv_id)] if arxiv_id else []
        if doi := _text(entry, "arxiv:doi"):
            external_ids.append(ExternalPaperId(provider="doi", value=doi))

        candidates.append(
            PaperCandidate(
                title=title,
                kind=CandidateKind.preprint,
                status=CandidateStatus.needs_manual_review,
                external_ids=external_ids,
                authors=authors,
                abstract=_text(entry, "atom:summary"),
                publication_date=_date(_text(entry, "atom:published")),
                source_url=abstract_url,
                pdf_url=pdf_url,
                landing_page_url=abstract_url,
                confidence=0.9 if query.provider_hint == "arxiv" else 0.75,
                discovery_paths=[
                    DiscoveryPath(
                        provider=SourceProvider.arxiv,
                        query=query.query,
                        source_candidate_uuid=query.source_candidate_uuid,
                        result_rank=rank,
                        url=abstract_url,
                    )
                ],
                raw_provider_data={"provider": "arxiv", "id": arxiv_id},
            )
        )

    return candidates


class ArxivClient:
    def __init__(
        self,
        http_client: httpx.Client | None = None,
        base_url: str = "https://export.arxiv.org/api/query",
        max_results: int = 10,
    ) -> None:
        self.http_client = http_client or httpx.Client()
        self.base_url = base_url
        self.max_results = max_results

    def search(self, query: DiscoveryQuery) -> list[PaperCandidate]:
        params = {"start": 0, "max_results": self.max_results, "sortBy": "relevance"}
        if query.provider_hint == "arxiv" and query.query.lower().startswith("arxiv:"):
            params["id_list"] = query.query.split(":", 1)[1]
        else:
            params["search_query"] = query.query

        response = self.http_client.get(self.base_url, params=params)
        response.raise_for_status()
        return parse_arxiv_atom(response.text, query)
