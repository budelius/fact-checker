from uuid import uuid4

from app.evaluation.evidence import NO_DIRECT_EVIDENCE_NOTE, select_claim_evidence
from app.schemas.claims import ExtractedClaim
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    GroundTruthJob,
    PaperCandidate,
    PaperChunk,
    PaperMetadata,
    PaperSummary,
    SourceDecision,
)
from app.schemas.ingestion import JobLifecycleStatus


def _claim() -> ExtractedClaim:
    return ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt="The creator says transformers parallelize sequence modeling.",
        claim_text="Transformers parallelize sequence modeling.",
    )


def _job_with_chunk(claim: ExtractedClaim) -> GroundTruthJob:
    paper_uuid = uuid4()
    chunk_uuid = uuid4()
    rejected_uuid = uuid4()
    return GroundTruthJob(
        ingestion_job_uuid=uuid4(),
        status=JobLifecycleStatus.succeeded,
        candidates=[
            PaperCandidate(
                uuid=paper_uuid,
                title="Attention Is All You Need",
                kind=CandidateKind.preprint,
                status=CandidateStatus.selected_ground_truth,
                source_url="https://arxiv.org/abs/1706.03762",
            ),
            PaperCandidate(
                uuid=rejected_uuid,
                title="Attention blog",
                kind=CandidateKind.non_paper,
                status=CandidateStatus.supplemental,
                source_url="https://example.com/blog",
            ),
        ],
        decisions=[
            SourceDecision(
                claim_uuid=claim.uuid,
                candidate_uuid=paper_uuid,
                status=CandidateStatus.selected_ground_truth,
                reason="paper selected",
            ),
            SourceDecision(
                claim_uuid=claim.uuid,
                candidate_uuid=rejected_uuid,
                status=CandidateStatus.supplemental,
                reason="supplemental context only",
            ),
        ],
        papers=[
            PaperMetadata(
                uuid=paper_uuid,
                title="Attention Is All You Need",
                publication_status="preprint",
                source_links=["https://arxiv.org/abs/1706.03762"],
            )
        ],
        chunks=[
            PaperChunk(
                uuid=chunk_uuid,
                paper_uuid=paper_uuid,
                source_uuid=paper_uuid,
                chunk_id="chunk-1",
                text="The Transformer allows significantly more parallelization.",
                page_start=1,
                page_end=1,
                section="Abstract",
                vault_path="vault/wiki/papers/attention-is-all-you-need.md",
                source_url="https://arxiv.org/abs/1706.03762",
            )
        ],
        summaries=[
            PaperSummary(
                paper_uuid=paper_uuid,
                summary_markdown="Generated summary that must not be used as verdict evidence.",
            )
        ],
    )


def test_selector_returns_raw_paper_chunks_and_source_metadata():
    claim = _claim()
    result = select_claim_evidence([claim], _job_with_chunk(claim))
    evidence = result[claim.uuid].candidates[0]

    assert evidence.raw_text == "The Transformer allows significantly more parallelization."
    assert evidence.title == "Attention Is All You Need"
    assert evidence.chunk_id == "chunk-1"
    assert evidence.page_start == 1
    assert evidence.section == "Abstract"
    assert evidence.is_preprint is True
    assert evidence.source_url == "https://arxiv.org/abs/1706.03762"


def test_selector_excludes_paper_summary_text_from_candidate_evidence():
    claim = _claim()
    result = select_claim_evidence([claim], _job_with_chunk(claim))
    serialized = str(result[claim.uuid].model_dump(mode="json"))

    assert "Generated summary that must not be used as verdict evidence" not in serialized
    assert "The Transformer allows significantly more parallelization" in serialized


def test_selector_preserves_unused_rejected_or_supplemental_candidates():
    claim = _claim()
    result = select_claim_evidence([claim], _job_with_chunk(claim))
    unused = result[claim.uuid].unused_candidates

    assert len(unused) == 1
    assert unused[0].title == "Attention blog"
    assert unused[0].selection_status == CandidateStatus.supplemental
    assert unused[0].source_url == "https://example.com/blog"


def test_selector_returns_no_direct_evidence_note_for_no_paper_case():
    claim = _claim()
    job = GroundTruthJob(
        ingestion_job_uuid=uuid4(),
        decisions=[
            SourceDecision(
                claim_uuid=claim.uuid,
                status=CandidateStatus.no_paper_found,
                reason="No scientific evidence found for now.",
            )
        ],
    )

    result = select_claim_evidence([claim], job)

    assert result[claim.uuid].candidates == []
    assert result[claim.uuid].notes == [NO_DIRECT_EVIDENCE_NOTE]
