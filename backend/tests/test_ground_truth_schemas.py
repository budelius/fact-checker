from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    GroundTruthArtifact,
    GroundTruthJob,
    GroundTruthStage,
    GroundTruthStageName,
    PaperChunk,
    PaperProcessingStatus,
    SourceProvider,
)


def test_ground_truth_stage_values():
    assert [stage.value for stage in GroundTruthStageName] == [
        "load_claims",
        "generate_queries",
        "search_openai_web",
        "search_paper_indexes",
        "merge_candidates",
        "select_sources",
        "acquire_papers",
        "parse_papers",
        "summarize_papers",
        "index_chunks",
        "write_owned_artifacts",
    ]


def test_source_provider_values():
    assert [provider.value for provider in SourceProvider] == [
        "phase2_hint",
        "openai_web",
        "arxiv",
        "openalex",
        "semantic_scholar",
    ]


def test_candidate_kind_values():
    assert [kind.value for kind in CandidateKind] == [
        "paper",
        "preprint",
        "non_paper",
        "unknown",
    ]


def test_candidate_status_values():
    assert [status.value for status in CandidateStatus] == [
        "selected_ground_truth",
        "rejected",
        "supplemental",
        "no_paper_found",
        "needs_manual_review",
    ]
    assert CandidateStatus.no_paper_found.value == "no_paper_found"


def test_paper_processing_status_values():
    assert [status.value for status in PaperProcessingStatus] == [
        "metadata_only",
        "linked",
        "downloaded",
        "parsed",
        "chunked",
        "summarized",
        "indexed",
        "failed",
    ]


def test_ground_truth_job_defaults_stage_and_artifact_lists():
    job = GroundTruthJob(ingestion_job_uuid=uuid4())

    assert job.stages == []
    assert job.artifacts == []
    assert job.current_operation == "Waiting to start ground-truth discovery."


def test_ground_truth_stage_and_artifact_models():
    stage = GroundTruthStage(name=GroundTruthStageName.merge_candidates)
    artifact = GroundTruthArtifact(
        artifact_type="paper_pdf",
        vault_path="vault/raw/papers/attention-is-all-you-need.pdf",
    )

    assert stage.status.value == "pending"
    assert artifact.metadata == {}


def test_paper_chunk_requires_trace_fields():
    with pytest.raises(ValidationError):
        PaperChunk()  # type: ignore[call-arg]

    chunk = PaperChunk(
        paper_uuid=UUID("00000000-0000-4000-8000-000000000001"),
        source_uuid=UUID("00000000-0000-4000-8000-000000000002"),
        chunk_id="paper-0001-0001",
        text="Scaled dot-product attention.",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        source_url="https://arxiv.org/abs/1706.03762",
    )

    assert chunk.paper_uuid == UUID("00000000-0000-4000-8000-000000000001")
    assert chunk.source_uuid == UUID("00000000-0000-4000-8000-000000000002")
    assert chunk.chunk_id == "paper-0001-0001"
    assert chunk.vault_path == "vault/wiki/papers/attention-is-all-you-need.md"
