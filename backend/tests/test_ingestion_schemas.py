from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.schemas.claims import EvidenceStatus, ExtractedClaim
from app.schemas.ingestion import (
    ArtifactType,
    IngestionJob,
    IngestionStage,
    IngestionStageName,
    JobLifecycleStatus,
    ResearchBasisStatus,
    SourceKind,
    StageStatus,
    TranscriptArtifact,
    TranscriptProvenance,
    TranscriptRetrievalMethod,
    TranscriptSegment,
)


def test_ingestion_stage_enum_values():
    assert [status.value for status in JobLifecycleStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
    ]
    assert [status.value for status in StageStatus] == [
        "pending",
        "running",
        "succeeded",
        "failed",
        "skipped",
    ]
    assert [kind.value for kind in SourceKind] == [
        "tiktok_url",
        "uploaded_video",
        "fixture_transcript",
    ]
    assert [stage.value for stage in IngestionStageName] == [
        "validate_url",
        "read_public_metadata",
        "build_transcript",
        "capture_source_clues",
        "extract_claims",
        "triage_research_basis",
        "write_owned_artifacts",
    ]
    assert [artifact.value for artifact in ArtifactType] == [
        "public_metadata",
        "transcript",
        "media_retrieval",
        "screenshot",
        "claims",
        "research_basis",
    ]
    assert [method.value for method in TranscriptRetrievalMethod] == [
        "public_caption",
        "subtitle_file",
        "transcription",
        "pasted",
        "fixture",
    ]
    assert [status.value for status in ResearchBasisStatus] == [
        "source_candidates_found",
        "no_research_source_found",
        "opinion_or_unratable",
        "needs_manual_review",
    ]


def test_ingestion_job_accepts_uploaded_video_source_kind():
    job = IngestionJob(
        source_kind=SourceKind.uploaded_video,
        source_url="uploaded://fixture.mp4",
        stages=[IngestionStage(name=IngestionStageName.build_transcript)],
    )

    assert isinstance(job.job_uuid, UUID)
    assert job.source_kind is SourceKind.uploaded_video
    assert job.stages[0].name is IngestionStageName.build_transcript


def test_transcript_artifact_fixture_segments():
    video_uuid = uuid4()
    artifact = TranscriptArtifact(
        video_uuid=video_uuid,
        provenance=TranscriptProvenance(
            method=TranscriptRetrievalMethod.fixture,
            source_url="https://www.tiktok.com/@fixture/video/1234567890",
        ),
        segments=[
            TranscriptSegment(
                start_seconds=1.0,
                end_seconds=4.0,
                text="Attention heads can specialize during training.",
            )
        ],
        plain_text="Attention heads can specialize during training.",
    )

    assert artifact.video_uuid == video_uuid
    assert artifact.provenance.method is TranscriptRetrievalMethod.fixture
    assert artifact.segments[0].start_seconds == 1.0


def test_extracted_claim_evidence_status_is_pending():
    claim = ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt="The paper showed attention scales well.",
        claim_text="Attention scales well in sequence models.",
    )

    assert claim.evidence_status is EvidenceStatus.pending


def test_extracted_claim_rejects_invalid_uuid():
    with pytest.raises(ValidationError):
        ExtractedClaim(
            source_video_uuid="not-a-uuid",
            source_transcript_uuid=uuid4(),
            transcript_excerpt="The paper showed attention scales well.",
            claim_text="Attention scales well in sequence models.",
        )
