from collections.abc import Iterable
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.claims import ExtractedClaim
from app.schemas.ingestion import ResearchBasisCandidate, ResearchBasisTriage, ScreenshotArtifact


class DiscoveryQuery(BaseModel):
    query: str
    provider_hint: str | None = None
    source_candidate_uuid: UUID | None = None
    claim_uuid: UUID | None = None
    reason: list[str] = Field(default_factory=list)


def _normalize_space(value: str) -> str:
    return " ".join(value.strip().split())


def _candidate_values(
    research_basis: ResearchBasisTriage | Iterable[ResearchBasisCandidate] | None,
) -> list[ResearchBasisCandidate]:
    if research_basis is None:
        return []
    if isinstance(research_basis, ResearchBasisTriage):
        return list(research_basis.candidates)
    return list(research_basis)


def _add_query(
    queries: list[DiscoveryQuery],
    by_query: dict[str, DiscoveryQuery],
    *,
    query: str,
    provider_hint: str | None,
    reason: str,
    source_candidate_uuid: UUID | None = None,
    claim_uuid: UUID | None = None,
) -> None:
    normalized_query = _normalize_space(query)
    if not normalized_query:
        return

    existing = by_query.get(normalized_query)
    if existing is not None:
        if reason not in existing.reason:
            existing.reason.append(reason)
        if existing.source_candidate_uuid is None and source_candidate_uuid is not None:
            existing.source_candidate_uuid = source_candidate_uuid
        if existing.claim_uuid is None and claim_uuid is not None:
            existing.claim_uuid = claim_uuid
        if existing.provider_hint is None and provider_hint is not None:
            existing.provider_hint = provider_hint
        return

    discovery_query = DiscoveryQuery(
        query=normalized_query,
        provider_hint=provider_hint,
        source_candidate_uuid=source_candidate_uuid,
        claim_uuid=claim_uuid,
        reason=[reason],
    )
    by_query[normalized_query] = discovery_query
    queries.append(discovery_query)


def build_discovery_queries(
    claims: Iterable[ExtractedClaim],
    research_basis: ResearchBasisTriage | Iterable[ResearchBasisCandidate] | None,
    screenshots: Iterable[ScreenshotArtifact] | None = None,
) -> list[DiscoveryQuery]:
    """Build deterministic source-discovery queries from Phase 2 handoff data."""
    queries: list[DiscoveryQuery] = []
    by_query: dict[str, DiscoveryQuery] = {}
    candidates = _candidate_values(research_basis)

    for candidate_type in ("doi", "arxiv", "url"):
        for candidate in candidates:
            if candidate.candidate_type.lower() != candidate_type:
                continue
            value = _normalize_space(candidate.value)
            if candidate_type == "doi":
                query = value
                reason = "exact doi identifier from Phase 2 source candidate"
            elif candidate_type == "arxiv":
                query = f"arxiv:{value.removeprefix('arXiv:').removeprefix('arxiv:')}"
                reason = "exact arxiv identifier from Phase 2 source candidate"
            else:
                query = value
                reason = "source URL from Phase 2 source candidate"

            _add_query(
                queries,
                by_query,
                query=query,
                provider_hint=candidate_type,
                source_candidate_uuid=candidate.uuid,
                reason=reason,
            )

    for candidate in candidates:
        if candidate.candidate_type.lower() != "paper_title":
            continue
        title = _normalize_space(candidate.value)
        if not title:
            continue
        _add_query(
            queries,
            by_query,
            query=f'"{title}"',
            provider_hint="paper_title",
            source_candidate_uuid=candidate.uuid,
            reason="quoted paper_title source candidate",
        )

    for claim in claims:
        _add_query(
            queries,
            by_query,
            query=claim.claim_text,
            provider_hint="claim",
            claim_uuid=claim.uuid,
            reason="semantic claim query from ExtractedClaim.claim_text",
        )
        _add_query(
            queries,
            by_query,
            query=claim.transcript_excerpt,
            provider_hint="transcript",
            claim_uuid=claim.uuid,
            reason="transcript excerpt query from ExtractedClaim.transcript_excerpt",
        )

    for screenshot in screenshots or []:
        if not screenshot.source_clue_text:
            continue
        _add_query(
            queries,
            by_query,
            query=screenshot.source_clue_text,
            provider_hint="source_clue_text",
            reason="screenshot source_clue_text query",
        )

    return queries
