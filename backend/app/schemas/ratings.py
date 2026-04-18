from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RatingTargetType(str, Enum):
    creator = "creator"
    paper = "paper"
    author = "author"
    source = "source"


class RatingBadge(str, Enum):
    strong_evidence_history = "strong evidence history"
    mixed_evidence_history = "mixed evidence history"
    limited_evidence = "limited evidence"
    insufficient_history = "insufficient history"


class RatingConfidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RatingBasis(BaseModel):
    evidence_count: int
    label_distribution: dict[str, int] = Field(default_factory=dict)
    source_basis: list[str] = Field(default_factory=list)
    report_version_uuids: list[UUID] = Field(default_factory=list)
    evidence_uuids: list[UUID] = Field(default_factory=list)
    relationship_uuids: list[UUID] = Field(default_factory=list)


class RatingRecord(BaseModel):
    rating_uuid: UUID = Field(default_factory=uuid4)
    target_uuid: UUID
    target_entity_type: RatingTargetType
    target_title: str
    badge: RatingBadge
    experimental: bool
    evidence_count: int
    label_distribution: dict[str, int] = Field(default_factory=dict)
    source_basis: list[str] = Field(default_factory=list)
    confidence_level: RatingConfidence
    report_version_uuids: list[UUID] = Field(default_factory=list)
    evidence_uuids: list[UUID] = Field(default_factory=list)
    relationship_uuids: list[UUID] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vault_path: str


class RatingMarkdownRecord(BaseModel):
    record: RatingRecord
    markdown: str
    vault_path: str
