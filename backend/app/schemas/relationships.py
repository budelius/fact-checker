from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RelationshipType(str, Enum):
    cites = "cites"
    supports = "supports"
    contradicts = "contradicts"
    authored_by = "authored_by"
    discussed_in = "discussed_in"
    derived_from = "derived_from"
    related_to = "related_to"


class KnowledgeRelationship(BaseModel):
    uuid: UUID
    relationship_type: RelationshipType
    source_uuid: UUID
    target_uuid: UUID
    provenance: str
    created_at: datetime
