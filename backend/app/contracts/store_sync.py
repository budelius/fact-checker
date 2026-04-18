MONGODB_ENTITY_COLLECTION = "entities"
MONGODB_RELATIONSHIP_COLLECTION = "relationships"
QDRANT_REQUIRED_PAYLOAD_KEYS = (
    "uuid",
    "entity_type",
    "vault_path",
    "chunk_id",
    "source",
    "source_date",
    "relationship_uuids",
)


def build_trace_keys(
    uuid: str,
    entity_type: str,
    vault_path: str,
    chunk_id: str,
    source: str,
    source_date: str | None = None,
    relationship_uuids: list[str] | None = None,
) -> dict[str, str | list[str] | None]:
    return {
        "uuid": uuid,
        "entity_type": entity_type,
        "vault_path": vault_path,
        "chunk_id": chunk_id,
        "source": source,
        "source_date": source_date,
        "relationship_uuids": relationship_uuids or [],
    }
