from uuid import UUID

from pydantic import BaseModel

from app.schemas.entities import EntityType


class QdrantPayload(BaseModel):
    uuid: UUID
    entity_type: EntityType
    vault_path: str
    chunk_id: str
    source_uuid: UUID | None = None
    relationship_uuid: UUID | None = None
