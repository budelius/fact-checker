from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.entities import EntityType


class QdrantPayload(BaseModel):
    uuid: UUID
    entity_type: EntityType
    vault_path: str
    chunk_id: str
    source: str
    source_date: date | None = None
    source_uuid: UUID | None = None
    relationship_uuid: UUID | None = None
    relationship_uuids: list[UUID] = Field(default_factory=list)
