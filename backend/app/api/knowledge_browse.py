from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.ground_truth import get_repository, get_vault_root
from app.knowledge.annotations import create_annotation, list_annotations_for_entity
from app.knowledge.vault import get_vault_note, list_vault_notes, list_vault_sections
from app.schemas.entities import EntityType
from app.schemas.knowledge import (
    KnowledgeAnnotation,
    KnowledgeAnnotationCreate,
    KnowledgeNoteDetail,
    KnowledgeNoteListItem,
    KnowledgeSection,
)

router = APIRouter(tags=["knowledge"])


@router.get("/sections", response_model=list[KnowledgeSection])
def fetch_sections(vault_root: Path = Depends(get_vault_root)) -> list[KnowledgeSection]:
    return list_vault_sections(vault_root)


@router.get("/notes", response_model=list[KnowledgeNoteListItem])
def fetch_notes(
    entity_type: EntityType | None = None,
    vault_root: Path = Depends(get_vault_root),
) -> list[KnowledgeNoteListItem]:
    return list_vault_notes(vault_root, entity_type=entity_type)


@router.get("/notes/{note_uuid}", response_model=KnowledgeNoteDetail)
def fetch_note(
    note_uuid: UUID,
    repository=Depends(get_repository),
    vault_root: Path = Depends(get_vault_root),
) -> KnowledgeNoteDetail:
    note = get_vault_note(vault_root, note_uuid=note_uuid)
    if note is None:
        raise HTTPException(status_code=404, detail="knowledge_note_not_found")
    note.annotations = list_annotations_for_entity(note.uuid, repository=repository)
    return note


@router.post("/notes/{note_uuid}/annotations", response_model=KnowledgeAnnotation)
def add_annotation(
    note_uuid: UUID,
    annotation: KnowledgeAnnotationCreate,
    repository=Depends(get_repository),
    vault_root: Path = Depends(get_vault_root),
) -> KnowledgeAnnotation:
    note = get_vault_note(vault_root, note_uuid=note_uuid)
    if note is None:
        raise HTTPException(status_code=404, detail="knowledge_note_not_found")
    return create_annotation(note.uuid, annotation.body, repository=repository)
