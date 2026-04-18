from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.entities import EntityType


class ConsistencyStatus(str, Enum):
    synced = "synced"
    drift = "drift"
    broken = "broken"


class RatingBadge(str, Enum):
    strong_evidence_history = "strong evidence history"
    mixed_evidence_history = "mixed evidence history"
    limited_evidence = "limited evidence"
    insufficient_history = "insufficient history"


class KnowledgeSection(BaseModel):
    name: str
    entity_type: EntityType | None = None
    count: int


class KnowledgeNoteListItem(BaseModel):
    uuid: UUID
    entity_type: EntityType
    title: str
    vault_path: str
    slug: str | None = None
    excerpt: str = ""
    updated_at: datetime | None = None


class KnowledgeRelationshipView(BaseModel):
    uuid: UUID | None = None
    relationship_type: str
    source_uuid: UUID | None = None
    target_uuid: UUID | None = None
    source_title: str | None = None
    target_title: str | None = None
    direction: str | None = None
    provenance: str | None = None
    vault_path: str | None = None


class KnowledgeBacklink(BaseModel):
    uuid: UUID
    entity_type: EntityType
    title: str
    vault_path: str
    relationship_type: str | None = None


class KnowledgeAnnotation(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    target_entity_uuid: UUID
    author: str = "user"
    body: str
    created_at: datetime
    updated_at: datetime


class KnowledgeAnnotationCreate(BaseModel):
    body: str


class KnowledgeRatingSummary(BaseModel):
    rating_uuid: UUID | None = None
    target_uuid: UUID
    target_entity_type: EntityType
    title: str | None = None
    vault_path: str | None = None
    badge: RatingBadge
    experimental: bool
    evidence_count: int
    label_distribution: dict[str, int] = Field(default_factory=dict)
    source_basis: list[str] = Field(default_factory=list)
    confidence_level: str
    report_version_uuids: list[UUID] = Field(default_factory=list)


class KnowledgeConsistencyIssue(BaseModel):
    status: ConsistencyStatus
    affected_uuid: UUID | None = None
    entity_type: EntityType | None = None
    title: str | None = None
    vault_path: str | None = None
    store: str
    issue: str
    suggested_repair: str


class KnowledgeConsistencySummary(BaseModel):
    status: ConsistencyStatus
    checked_notes: int = 0
    missing_mongo_records: int = 0
    missing_qdrant_payloads: int = 0
    broken_relationships: int = 0
    orphan_vectors: int = 0
    issues: list[KnowledgeConsistencyIssue] = Field(default_factory=list)


class KnowledgeNoteDetail(BaseModel):
    uuid: UUID
    entity_type: EntityType
    title: str
    vault_path: str
    slug: str | None = None
    frontmatter: dict[str, Any] = Field(default_factory=dict)
    body_markdown: str
    wiki_links: list[str] = Field(default_factory=list)
    relationships: list[KnowledgeRelationshipView] = Field(default_factory=list)
    backlinks: list[KnowledgeBacklink] = Field(default_factory=list)
    annotations: list[KnowledgeAnnotation] = Field(default_factory=list)
    rating: KnowledgeRatingSummary | None = None
    consistency: KnowledgeConsistencySummary | None = None
    updated_at: datetime | None = None


class KnowledgeSearchResult(BaseModel):
    uuid: UUID
    entity_type: EntityType
    title: str
    vault_path: str
    snippet: str
    score: float | None = None
    source: str | None = None
    chunk_id: str | None = None
    source_uuid: UUID | None = None
    relationship_uuid: UUID | None = None
    relationship_uuids: list[UUID] = Field(default_factory=list)
    vector_backed: bool = False


class KnowledgeGraphNode(BaseModel):
    uuid: UUID
    entity_type: EntityType
    title: str
    vault_path: str | None = None
    degree: int = 0


class KnowledgeGraphEdge(BaseModel):
    uuid: UUID
    relationship_type: str
    source_uuid: UUID
    target_uuid: UUID
    provenance: str
    direction: str


class KnowledgeGraphResponse(BaseModel):
    selected_uuid: UUID
    nodes: list[KnowledgeGraphNode] = Field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = Field(default_factory=list)
    important_nodes: list[KnowledgeGraphNode] = Field(default_factory=list)
    clusters: dict[str, list[UUID]] = Field(default_factory=dict)
