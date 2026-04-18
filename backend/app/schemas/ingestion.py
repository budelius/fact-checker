from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobLifecycleStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class StageStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    skipped = "skipped"


class SourceKind(str, Enum):
    tiktok_url = "tiktok_url"
    uploaded_video = "uploaded_video"
    fixture_transcript = "fixture_transcript"


class IngestionStageName(str, Enum):
    validate_url = "validate_url"
    read_public_metadata = "read_public_metadata"
    build_transcript = "build_transcript"
    capture_source_clues = "capture_source_clues"
    extract_claims = "extract_claims"
    triage_research_basis = "triage_research_basis"
    write_owned_artifacts = "write_owned_artifacts"


class ArtifactType(str, Enum):
    public_metadata = "public_metadata"
    transcript = "transcript"
    media_retrieval = "media_retrieval"
    screenshot = "screenshot"
    claims = "claims"
    research_basis = "research_basis"


class TranscriptRetrievalMethod(str, Enum):
    public_caption = "public_caption"
    subtitle_file = "subtitle_file"
    transcription = "transcription"
    pasted = "pasted"
    fixture = "fixture"


class ResearchBasisStatus(str, Enum):
    source_candidates_found = "source_candidates_found"
    no_research_source_found = "no_research_source_found"
    opinion_or_unratable = "opinion_or_unratable"
    needs_manual_review = "needs_manual_review"


class IngestionStage(BaseModel):
    name: IngestionStageName
    status: StageStatus = StageStatus.pending
    message: str = ""
    entity_uuid: UUID | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ArtifactStatus(BaseModel):
    artifact_type: ArtifactType
    status: StageStatus
    label: str
    entity_uuid: UUID | None = None
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class TranscriptSegment(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    start_seconds: float | None = None
    end_seconds: float | None = None
    text: str


class TranscriptProvenance(BaseModel):
    method: TranscriptRetrievalMethod
    source_url: str
    source_artifact_uuid: UUID | None = None
    provider: str | None = None
    confidence: float | None = None
    quality_note: str | None = None
    failure_reason: str | None = None


class TranscriptArtifact(BaseModel):
    transcript_uuid: UUID = Field(default_factory=uuid4)
    video_uuid: UUID
    provenance: TranscriptProvenance
    segments: list[TranscriptSegment] = Field(default_factory=list)
    plain_text: str
    vault_path: str | None = None


class ScreenshotArtifact(BaseModel):
    screenshot_uuid: UUID = Field(default_factory=uuid4)
    video_uuid: UUID
    timestamp_seconds: float | None = None
    vault_path: str
    asset_url: str | None = None
    source_clue: bool = False
    source_clue_text: str | None = None
    claim_uuids: list[UUID] = Field(default_factory=list)


class ResearchBasisCandidate(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    candidate_type: str
    value: str
    source: str
    source_uuid: UUID | None = None
    confidence: float | None = None


class ResearchBasisTriage(BaseModel):
    status: ResearchBasisStatus
    candidates: list[ResearchBasisCandidate] = Field(default_factory=list)
    reason: str

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)


class IngestionJob(BaseModel):
    job_uuid: UUID = Field(default_factory=uuid4)
    source_kind: SourceKind
    source_url: str
    status: JobLifecycleStatus = JobLifecycleStatus.pending
    current_operation: str = "Waiting to start ingestion."
    stages: list[IngestionStage] = Field(default_factory=list)
    artifacts: list[ArtifactStatus] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error_message: str | None = None
    video_uuid: UUID | None = None
