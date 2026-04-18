from pathlib import Path
from uuid import UUID

from app.knowledge.vault import get_vault_note, list_vault_notes
from app.schemas.knowledge import (
    ConsistencyStatus,
    KnowledgeConsistencyIssue,
    KnowledgeConsistencySummary,
)


def _entities(repository) -> dict[str, dict]:
    if repository is None or not hasattr(repository, "list_entities"):
        return {}
    return {str(entity["uuid"]): entity for entity in repository.list_entities()}


def _relationships(repository) -> list[dict]:
    if repository is None or not hasattr(repository, "list_relationships"):
        return []
    return repository.list_relationships()


def _payloads(qdrant_repository) -> list[dict]:
    if qdrant_repository is None or not hasattr(qdrant_repository, "scroll_payloads"):
        return []
    return qdrant_repository.scroll_payloads()


def _summary_status(issues: list[KnowledgeConsistencyIssue]) -> ConsistencyStatus:
    if any(issue.status == ConsistencyStatus.broken for issue in issues):
        return ConsistencyStatus.broken
    if issues:
        return ConsistencyStatus.drift
    return ConsistencyStatus.synced


def check_knowledge_consistency(vault_root: Path, repository, qdrant_repository) -> KnowledgeConsistencySummary:
    notes = list_vault_notes(vault_root)
    note_by_uuid = {str(note.uuid): note for note in notes}
    note_by_path = {note.vault_path: note for note in notes}
    entities = _entities(repository)
    relationships = _relationships(repository)
    payloads = _payloads(qdrant_repository)
    payload_uuids = {str(payload.get("uuid")) for payload in payloads if payload.get("uuid")}
    payload_paths = {str(payload.get("vault_path")) for payload in payloads if payload.get("vault_path")}

    issues: list[KnowledgeConsistencyIssue] = []
    missing_mongo_records = 0
    missing_qdrant_payloads = 0
    broken_relationships = 0
    orphan_vectors = 0

    for note in notes:
        entity = entities.get(str(note.uuid))
        if entity is None:
            missing_mongo_records += 1
            issues.append(
                KnowledgeConsistencyIssue(
                    status=ConsistencyStatus.broken,
                    affected_uuid=note.uuid,
                    entity_type=note.entity_type,
                    title=note.title,
                    vault_path=note.vault_path,
                    store="mongodb",
                    issue="Markdown note has no matching MongoDB entity record.",
                    suggested_repair="Reindex the Markdown note into the entities collection.",
                )
            )
        elif entity.get("vault_path") and entity.get("vault_path") != note.vault_path:
            issues.append(
                KnowledgeConsistencyIssue(
                    status=ConsistencyStatus.drift,
                    affected_uuid=note.uuid,
                    entity_type=note.entity_type,
                    title=note.title,
                    vault_path=note.vault_path,
                    store="mongodb",
                    issue="MongoDB entity vault_path differs from Markdown path.",
                    suggested_repair="Update the entity vault_path or move the Markdown note.",
                )
            )

        if str(note.uuid) not in payload_uuids and note.vault_path not in payload_paths:
            missing_qdrant_payloads += 1
            issues.append(
                KnowledgeConsistencyIssue(
                    status=ConsistencyStatus.drift,
                    affected_uuid=note.uuid,
                    entity_type=note.entity_type,
                    title=note.title,
                    vault_path=note.vault_path,
                    store="qdrant",
                    issue="Markdown note has no matching Qdrant payload.",
                    suggested_repair="Reindex the note or source chunks into Qdrant.",
                )
            )

    known_uuids = set(note_by_uuid) | set(entities)
    for relationship in relationships:
        source_uuid = str(relationship.get("source_uuid"))
        target_uuid = str(relationship.get("target_uuid"))
        if source_uuid not in known_uuids or target_uuid not in known_uuids:
            broken_relationships += 1
            issues.append(
                KnowledgeConsistencyIssue(
                    status=ConsistencyStatus.broken,
                    affected_uuid=relationship.get("uuid"),
                    store="mongodb",
                    issue="Relationship references a missing source or target entity.",
                    suggested_repair="Rebuild relationship edges after restoring missing entities.",
                )
            )

    for payload in payloads:
        payload_uuid = str(payload.get("uuid") or "")
        payload_path = str(payload.get("vault_path") or "")
        if payload_uuid not in known_uuids and payload_path not in note_by_path:
            orphan_vectors += 1
            issues.append(
                KnowledgeConsistencyIssue(
                    status=ConsistencyStatus.drift,
                    affected_uuid=UUID(payload_uuid) if payload_uuid else None,
                    store="qdrant",
                    issue="Qdrant payload has no matching Markdown or MongoDB entity.",
                    suggested_repair="Delete or regenerate the orphan vector payload.",
                )
            )

    return KnowledgeConsistencySummary(
        status=_summary_status(issues),
        checked_notes=len(notes),
        missing_mongo_records=missing_mongo_records,
        missing_qdrant_payloads=missing_qdrant_payloads,
        broken_relationships=broken_relationships,
        orphan_vectors=orphan_vectors,
        issues=issues,
    )
