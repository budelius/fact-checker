from collections.abc import Iterable
from typing import Any

from openai import OpenAI

from app.ground_truth.queries import DiscoveryQuery
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    DiscoveryPath,
    PaperCandidate,
    SourceProvider,
)
from app.settings import Settings


PAPER_URL_MARKERS = (
    "arxiv.org/abs/",
    "arxiv.org/pdf/",
    "openreview.net/forum",
    "aclanthology.org/",
    "proceedings.neurips.cc/",
    "proceedings.mlr.press/",
    "jmlr.org/",
)


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {}


def _scrub_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        scrubbed = {}
        for key, item in value.items():
            if key.lower() in {"api_key", "apikey", "authorization", "x-api-key"}:
                scrubbed[key] = "[redacted]"
            else:
                scrubbed[key] = _scrub_secrets(item)
        return scrubbed
    if isinstance(value, list):
        return [_scrub_secrets(item) for item in value]
    return value


def _walk_output_items(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for item in payload.get("output", []):
        if isinstance(item, dict):
            yield item


def _annotations(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for item in _walk_output_items(payload):
        for content in item.get("content", []) or []:
            for annotation in content.get("annotations", []) or []:
                if isinstance(annotation, dict):
                    yield annotation


def _sources(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for item in _walk_output_items(payload):
        if item.get("type") != "web_search_call":
            continue
        action = item.get("action") or {}
        for source in action.get("sources", []) or []:
            if isinstance(source, dict):
                yield source


def _is_paper_url(url: str) -> bool:
    normalized = url.lower()
    return any(marker in normalized for marker in PAPER_URL_MARKERS)


def _kind_for_url(url: str) -> CandidateKind:
    if "arxiv.org/" in url.lower() or "openreview.net/" in url.lower():
        return CandidateKind.preprint
    if _is_paper_url(url):
        return CandidateKind.paper
    return CandidateKind.non_paper


def _candidate_from_source(
    *,
    title: str,
    url: str,
    rank: int,
    query: DiscoveryQuery,
    raw_provider_data: dict[str, Any],
) -> PaperCandidate:
    kind = _kind_for_url(url)
    return PaperCandidate(
        title=title or url,
        kind=kind,
        status=(
            CandidateStatus.needs_manual_review
            if kind in {CandidateKind.paper, CandidateKind.preprint}
            else CandidateStatus.supplemental
        ),
        source_url=url,
        landing_page_url=url,
        pdf_url=url if url.lower().endswith(".pdf") else None,
        confidence=0.7 if kind != CandidateKind.non_paper else 0.35,
        discovery_paths=[
            DiscoveryPath(
                provider=SourceProvider.openai_web,
                query=query.query,
                source_candidate_uuid=query.source_candidate_uuid,
                result_rank=rank,
                url=url,
            )
        ],
        raw_provider_data=_scrub_secrets(raw_provider_data),
    )


def parse_openai_web_search_response(payload: dict[str, Any], query: DiscoveryQuery) -> list[PaperCandidate]:
    candidates: list[PaperCandidate] = []
    seen_urls: set[str] = set()

    for rank, annotation in enumerate(_annotations(payload), start=1):
        if annotation.get("type") != "url_citation":
            continue
        url = str(annotation.get("url") or "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        candidates.append(
            _candidate_from_source(
                title=str(annotation.get("title") or url),
                url=url,
                rank=rank,
                query=query,
                raw_provider_data={"annotation": annotation},
            )
        )

    offset = len(candidates)
    for rank, source in enumerate(_sources(payload), start=1):
        url = str(source.get("url") or "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        candidates.append(
            _candidate_from_source(
                title=str(source.get("title") or url),
                url=url,
                rank=offset + rank,
                query=query,
                raw_provider_data={"source": source},
            )
        )

    return candidates


class OpenAIWebSearchClient:
    def __init__(
        self,
        settings: Settings,
        client: OpenAI | None = None,
    ) -> None:
        self.settings = settings
        self.client = client or OpenAI(api_key=settings.openai_api_key)

    def search(self, query: DiscoveryQuery) -> list[PaperCandidate]:
        # The include path below must stay explicit so trace logs preserve complete web-search sources:
        # web_search_call.action.sources
        response = self.client.responses.create(
            model=self.settings.openai_discovery_model,
            tools=[{"type": "web_search"}],
            include=["web_search_call.action.sources"],
            input=(
                "Find paper or preprint candidates for this AI research claim. "
                "Return paper/preprint URLs first; non-paper pages are supplemental only.\n"
                f"Query: {query.query}"
            ),
        )
        return parse_openai_web_search_response(_as_dict(response), query)
