MONGODB_ENTITY_COLLECTION = "entities"
MONGODB_RELATIONSHIP_COLLECTION = "relationships"
QDRANT_REQUIRED_PAYLOAD_KEYS = ("uuid", "entity_type", "vault_path", "chunk_id")


def build_trace_keys(uuid: str, entity_type: str, vault_path: str) -> dict[str, str]:
    return {
        "uuid": uuid,
        "entity_type": entity_type,
        "vault_path": vault_path,
    }
