from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    video = "video"
    creator = "creator"
    transcript = "transcript"
    screenshot = "screenshot"
    claim = "claim"
    source = "source"
    paper = "paper"
    author = "author"
    evidence = "evidence"
    report = "report"
    rating = "rating"
    topic = "topic"


class ExternalId(BaseModel):
    provider: str
    value: str


class KnowledgeEntity(BaseModel):
    uuid: UUID
    entity_type: EntityType
    slug: str
    title: str
    vault_path: str
    aliases: list[str] = Field(default_factory=list)
    external_ids: list[ExternalId] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
