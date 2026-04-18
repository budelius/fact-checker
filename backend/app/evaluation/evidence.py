from collections import defaultdict
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.claims import ExtractedClaim
from app.schemas.evaluation import EvidenceCandidate, EvidenceSourceKind
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    GroundTruthJob,
    PaperCandidate,
    PaperChunk,
    PaperMetadata,
    SourceDecision,
)


NO_DIRECT_EVIDENCE_NOTE = "No direct scientific evidence was available for this claim."


class ClaimEvidenceSet(BaseModel):
    claim_uuid: UUID
    candidates: list[EvidenceCandidate] = Field(default_factory=list)
    unused_candidates: list[EvidenceCandidate] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def _claim_uuid(claim: ExtractedClaim | dict) -> UUID:
    if isinstance(claim, ExtractedClaim):
        return claim.uuid
    return UUID(str(claim["uuid"]))


def _claim_by_uuid(claims: list[ExtractedClaim | dict]) -> dict[UUID, ExtractedClaim | dict]:
    return {_claim_uuid(claim): claim for claim in claims}


def _candidate_source_kind(candidate: PaperCandidate | None) -> EvidenceSourceKind:
    if candidate is None:
        return EvidenceSourceKind.direct_source_text
    if candidate.kind in {CandidateKind.paper, CandidateKind.preprint}:
        return EvidenceSourceKind.paper_chunk
    if candidate.raw_provider_data.get("source_kind") == "news_article":
        return EvidenceSourceKind.news_article
    return EvidenceSourceKind.direct_source_text


def _is_preprint(metadata: PaperMetadata | None, candidate: PaperCandidate | None) -> bool:
    status = metadata.publication_status if metadata else candidate.kind.value if candidate else ""
    return status == CandidateKind.preprint.value


def _source_url(chunk: PaperChunk | None, candidate: PaperCandidate | None) -> str:
    if chunk and chunk.source_url:
        return chunk.source_url
    if candidate:
        for url in (candidate.source_url, candidate.landing_page_url, candidate.pdf_url):
            if url:
                return url
    return ""


def _candidate_for_chunk(
    *,
    claim_uuid: UUID,
    decision: SourceDecision,
    chunk: PaperChunk,
    candidate: PaperCandidate | None,
    metadata: PaperMetadata | None,
    excerpt_max_chars: int,
) -> EvidenceCandidate:
    title = metadata.title if metadata else candidate.title if candidate else chunk.chunk_id
    excerpt = chunk.text[:excerpt_max_chars]
    return EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=chunk.uuid,
        source_kind=_candidate_source_kind(candidate),
        title=title,
        raw_text=chunk.text,
        excerpt=excerpt,
        source_url=_source_url(chunk, candidate),
        paper_uuid=chunk.paper_uuid,
        source_uuid=chunk.source_uuid,
        candidate_uuid=decision.candidate_uuid,
        chunk_id=chunk.chunk_id,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        section=chunk.section,
        publication_status=metadata.publication_status if metadata else candidate.kind.value if candidate else None,
        is_preprint=_is_preprint(metadata, candidate),
        source_policy_notes=(
            ["Non-scientific source exception"]
            if _candidate_source_kind(candidate) == EvidenceSourceKind.news_article
            else []
        ),
        selection_status=decision.status.value,
        metadata={"decision_uuid": str(decision.uuid), "vault_path": chunk.vault_path},
    )


def _unused_candidate(
    *,
    claim_uuid: UUID,
    decision: SourceDecision,
    candidate: PaperCandidate | None,
) -> EvidenceCandidate:
    evidence_uuid = decision.candidate_uuid or decision.uuid
    title = candidate.title if candidate else decision.status.value
    source_url = _source_url(None, candidate)
    raw_text = candidate.abstract if candidate and candidate.abstract else decision.reason
    return EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=evidence_uuid,
        source_kind=_candidate_source_kind(candidate),
        title=title,
        raw_text=raw_text,
        excerpt=raw_text[:500],
        source_url=source_url,
        paper_uuid=decision.candidate_uuid,
        source_uuid=decision.candidate_uuid,
        candidate_uuid=decision.candidate_uuid,
        publication_status=candidate.kind.value if candidate else None,
        is_preprint=candidate.kind == CandidateKind.preprint if candidate else False,
        source_policy_notes=[],
        selection_status=decision.status.value,
        metadata={"decision_uuid": str(decision.uuid), "decision_reason": decision.reason},
    )


class EvidenceSelector:
    def __init__(
        self,
        *,
        max_chunks_per_claim: int = 8,
        excerpt_max_chars: int = 1200,
    ) -> None:
        self.max_chunks_per_claim = max_chunks_per_claim
        self.excerpt_max_chars = excerpt_max_chars

    def select(
        self,
        claims: list[ExtractedClaim | dict],
        ground_truth_job: GroundTruthJob,
    ) -> dict[UUID, ClaimEvidenceSet]:
        claim_map = _claim_by_uuid(claims)
        candidate_by_uuid = {candidate.uuid: candidate for candidate in ground_truth_job.candidates}
        paper_by_uuid = {paper.uuid: paper for paper in ground_truth_job.papers}
        chunks_by_paper_uuid: dict[UUID, list[PaperChunk]] = defaultdict(list)
        for chunk in ground_truth_job.chunks:
            chunks_by_paper_uuid[chunk.paper_uuid].append(chunk)

        selected_decisions: dict[UUID, list[SourceDecision]] = defaultdict(list)
        unused_decisions: dict[UUID, list[SourceDecision]] = defaultdict(list)
        for decision in ground_truth_job.decisions:
            if decision.claim_uuid is None:
                continue
            if decision.claim_uuid not in claim_map:
                continue
            if decision.status == CandidateStatus.selected_ground_truth:
                selected_decisions[decision.claim_uuid].append(decision)
            else:
                unused_decisions[decision.claim_uuid].append(decision)

        evidence_sets: dict[UUID, ClaimEvidenceSet] = {}
        for claim_uuid in claim_map:
            evidence_set = ClaimEvidenceSet(claim_uuid=claim_uuid)
            for decision in selected_decisions[claim_uuid]:
                if decision.candidate_uuid is None:
                    continue
                candidate = candidate_by_uuid.get(decision.candidate_uuid)
                metadata = paper_by_uuid.get(decision.candidate_uuid)
                chunks = chunks_by_paper_uuid.get(decision.candidate_uuid, [])
                for chunk in chunks[: self.max_chunks_per_claim - len(evidence_set.candidates)]:
                    evidence_set.candidates.append(
                        _candidate_for_chunk(
                            claim_uuid=claim_uuid,
                            decision=decision,
                            chunk=chunk,
                            candidate=candidate,
                            metadata=metadata,
                            excerpt_max_chars=self.excerpt_max_chars,
                        )
                    )
                if len(evidence_set.candidates) >= self.max_chunks_per_claim:
                    break

            for decision in unused_decisions[claim_uuid]:
                candidate = (
                    candidate_by_uuid.get(decision.candidate_uuid)
                    if decision.candidate_uuid
                    else None
                )
                evidence_set.unused_candidates.append(
                    _unused_candidate(claim_uuid=claim_uuid, decision=decision, candidate=candidate)
                )

            if not evidence_set.candidates:
                evidence_set.notes.append(NO_DIRECT_EVIDENCE_NOTE)
            evidence_sets[claim_uuid] = evidence_set

        return evidence_sets


def select_claim_evidence(
    claims: list[ExtractedClaim | dict],
    ground_truth_job: GroundTruthJob,
    *,
    max_chunks_per_claim: int = 8,
    excerpt_max_chars: int = 1200,
) -> dict[UUID, ClaimEvidenceSet]:
    return EvidenceSelector(
        max_chunks_per_claim=max_chunks_per_claim,
        excerpt_max_chars=excerpt_max_chars,
    ).select(claims, ground_truth_job)
