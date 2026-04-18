from pathlib import Path
from typing import Protocol
from uuid import UUID

from app.knowledge.vault import get_vault_note, list_vault_notes
from app.schemas.entities import EntityType
from app.schemas.knowledge import KnowledgeSearchResult


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


def _payload_uuid(payload: dict) -> UUID | None:
    raw_uuid = payload.get("uuid")
    if not raw_uuid:
        return None
    try:
        return UUID(str(raw_uuid))
    except ValueError:
        return None


def _payload_relationship_uuids(payload: dict) -> list[UUID]:
    values = payload.get("relationship_uuids") or []
    return [UUID(str(value)) for value in values]


def _snippet_from_note(vault_root: Path, entity_uuid: UUID, fallback: str) -> tuple[str, str]:
    note = get_vault_note(vault_root, note_uuid=entity_uuid)
    if note is None:
        return fallback, fallback
    first_line = next(
        (line.strip().lstrip("#").strip() for line in note.body_markdown.splitlines() if line.strip()),
        "",
    )
    return note.title, first_line[:320]


def _vector_results(
    *,
    query: str,
    qdrant_repository,
    embedding_provider: EmbeddingProvider,
    vault_root: Path,
    entity_types: list[str] | None,
    limit: int,
) -> list[KnowledgeSearchResult]:
    vector = embedding_provider.embed_texts([query])[0]
    matches = qdrant_repository.search_payloads(
        vector,
        limit=limit,
        entity_types=entity_types,
    )
    results = []
    for match in matches:
        payload = match.get("payload") or {}
        entity_uuid = _payload_uuid(payload)
        if entity_uuid is None:
            continue
        entity_type = EntityType(str(payload.get("entity_type")))
        fallback_title = str(payload.get("title") or payload.get("vault_path") or entity_uuid)
        title, snippet = _snippet_from_note(vault_root, entity_uuid, fallback_title)
        relationship_uuid = payload.get("relationship_uuid")
        results.append(
            KnowledgeSearchResult(
                uuid=entity_uuid,
                entity_type=entity_type,
                title=title,
                vault_path=str(payload.get("vault_path") or ""),
                snippet=payload.get("snippet") or snippet,
                score=match.get("score"),
                source=payload.get("source"),
                chunk_id=payload.get("chunk_id"),
                source_uuid=payload.get("source_uuid"),
                relationship_uuid=relationship_uuid,
                relationship_uuids=_payload_relationship_uuids(payload),
                vector_backed=True,
            )
        )
    return results


def _fallback_results(
    *,
    query: str,
    vault_root: Path,
    entity_types: list[str] | None,
    limit: int,
) -> list[KnowledgeSearchResult]:
    normalized = query.lower().strip()
    requested = {EntityType(value) for value in entity_types or []}
    results = []
    for note in list_vault_notes(vault_root):
        if requested and note.entity_type not in requested:
            continue
        detail = get_vault_note(vault_root, note_uuid=note.uuid)
        if detail is None:
            continue
        haystack = " ".join([detail.title, detail.vault_path, detail.body_markdown]).lower()
        if normalized and normalized not in haystack:
            continue
        results.append(
            KnowledgeSearchResult(
                uuid=detail.uuid,
                entity_type=detail.entity_type,
                title=detail.title,
                vault_path=detail.vault_path,
                snippet=note.excerpt or detail.body_markdown[:320],
                score=1.0 if normalized else 0.0,
                source="vault_fallback",
                vector_backed=False,
            )
        )
        if len(results) >= limit:
            break
    return results


def search_knowledge(
    query: str,
    *,
    qdrant_repository,
    embedding_provider: EmbeddingProvider | None,
    vault_root: Path,
    entity_types: list[str] | None = None,
    limit: int = 10,
) -> list[KnowledgeSearchResult]:
    if query.strip() and qdrant_repository is not None and embedding_provider is not None:
        results = _vector_results(
            query=query,
            qdrant_repository=qdrant_repository,
            embedding_provider=embedding_provider,
            vault_root=vault_root,
            entity_types=entity_types,
            limit=limit,
        )
        if results:
            return results

    return _fallback_results(
        query=query,
        vault_root=vault_root,
        entity_types=entity_types,
        limit=limit,
    )
