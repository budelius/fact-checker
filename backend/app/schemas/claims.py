from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EvidenceStatus(str, Enum):
    pending = "pending"


class ClaimExtractionStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class ExtractedClaim(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    source_video_uuid: UUID
    source_transcript_uuid: UUID
    timestamp_start_seconds: float | None = None
    timestamp_end_seconds: float | None = None
    transcript_excerpt: str
    claim_text: str
    screenshot_uuids: list[UUID] = Field(default_factory=list)
    extraction_confidence: float | None = None
    evidence_status: EvidenceStatus = EvidenceStatus.pending
    source_candidate_count: int = 0
