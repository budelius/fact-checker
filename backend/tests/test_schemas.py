from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.schemas.entities import EntityType, ExternalId, KnowledgeEntity
from app.schemas.relationships import KnowledgeRelationship, RelationshipType
from app.schemas.vector_payloads import QdrantPayload


NOW = datetime(2026, 4, 18, tzinfo=UTC)
ENTITY_UUID = UUID("00000000-0000-4000-8000-000000000001")
TARGET_UUID = UUID("00000000-0000-4000-8000-000000000002")
RELATIONSHIP_UUID = UUID("00000000-0000-4000-8000-000000000003")


def test_knowledge_entity_contract():
    entity = KnowledgeEntity(
        uuid=ENTITY_UUID,
        entity_type=EntityType.paper,
        slug="attention-is-all-you-need",
        title="Attention Is All You Need",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        aliases=["transformer-paper"],
        external_ids=[ExternalId(provider="arxiv", value="1706.03762")],
        created_at=NOW,
        updated_at=NOW,
    )

    assert entity.uuid == ENTITY_UUID
    assert entity.entity_type is EntityType.paper
    assert entity.external_ids[0].provider == "arxiv"


def test_relationship_contract():
    relationship = KnowledgeRelationship(
        uuid=RELATIONSHIP_UUID,
        relationship_type=RelationshipType.cites,
        source_uuid=ENTITY_UUID,
        target_uuid=TARGET_UUID,
        provenance="vault/wiki/papers/attention-is-all-you-need.md",
        created_at=NOW,
    )

    assert relationship.relationship_type is RelationshipType.cites
    assert relationship.source_uuid == ENTITY_UUID
    assert relationship.target_uuid == TARGET_UUID


def test_qdrant_payload_contract():
    payload = QdrantPayload(
        uuid=ENTITY_UUID,
        entity_type=EntityType.paper,
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        chunk_id="abstract-0001",
        source="arxiv:1706.03762",
        source_date="2017-06-12",
        source_uuid=TARGET_UUID,
        relationship_uuid=RELATIONSHIP_UUID,
        relationship_uuids=[RELATIONSHIP_UUID],
    )

    assert payload.uuid == ENTITY_UUID
    assert payload.entity_type is EntityType.paper
    assert payload.vault_path.endswith("attention-is-all-you-need.md")
    assert payload.source == "arxiv:1706.03762"
    assert payload.source_date.isoformat() == "2017-06-12"
    assert payload.relationship_uuids == [RELATIONSHIP_UUID]


def test_invalid_uuid_rejected():
    with pytest.raises(ValidationError):
        KnowledgeEntity(
            uuid="not-a-uuid",
            entity_type=EntityType.claim,
            slug="bad-uuid",
            title="Bad UUID",
            vault_path="vault/wiki/claims/bad-uuid.md",
            created_at=NOW,
            updated_at=NOW,
        )
