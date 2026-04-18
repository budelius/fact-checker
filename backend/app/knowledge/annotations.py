from datetime import datetime, timezone
from uuid import UUID

from app.schemas.knowledge import KnowledgeAnnotation

_ANNOTATION_STORE: dict[str, list[dict]] = {}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def serialize_annotation(annotation: KnowledgeAnnotation) -> dict:
    return annotation.model_dump(mode="json")


def create_annotation(
    target_entity_uuid: UUID,
    body: str,
    repository=None,
) -> KnowledgeAnnotation:
    now = utc_now()
    annotation = KnowledgeAnnotation(
        target_entity_uuid=target_entity_uuid,
        author="user",
        body=body,
        created_at=now,
        updated_at=now,
    )
    payload = serialize_annotation(annotation)
    if repository is not None and hasattr(repository, "upsert_annotation"):
        repository.upsert_annotation(payload)
    else:
        _ANNOTATION_STORE.setdefault(str(target_entity_uuid), []).append(payload)
    return annotation


def list_annotations_for_entity(
    target_entity_uuid: UUID,
    repository=None,
) -> list[KnowledgeAnnotation]:
    if repository is not None and hasattr(repository, "list_annotations"):
        return [
            KnowledgeAnnotation.model_validate(payload)
            for payload in repository.list_annotations(target_entity_uuid)
        ]
    return [
        KnowledgeAnnotation.model_validate(payload)
        for payload in _ANNOTATION_STORE.get(str(target_entity_uuid), [])
    ]


def clear_annotations_for_tests() -> None:
    _ANNOTATION_STORE.clear()
