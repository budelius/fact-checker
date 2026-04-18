"""Evidence-state rating routes."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.ground_truth import get_repository, get_vault_root
from app.knowledge.ratings import build_rating_record, write_rating_markdown
from app.schemas.entities import EntityType, KnowledgeEntity
from app.schemas.ratings import RatingRecord

router = APIRouter(tags=["knowledge-ratings"])

RATING_VAULT_PREFIX = "vault/wiki/ratings"
_RATING_STORE: dict[str, RatingRecord] = {}


def clear_ratings_for_tests() -> None:
    _RATING_STORE.clear()


def _reports_for_target(repository, target_uuid: UUID) -> list:
    if repository is not None and hasattr(repository, "list_reports_for_rating"):
        return repository.list_reports_for_rating(target_uuid)
    return []


def _relationships_for_target(repository, target_uuid: UUID) -> list:
    if repository is not None and hasattr(repository, "list_relationships"):
        return repository.list_relationships(source_uuid=target_uuid, target_uuid=target_uuid)
    return []


@router.get("/ratings/{target_uuid}", response_model=RatingRecord)
def fetch_rating(target_uuid: UUID) -> RatingRecord:
    rating = _RATING_STORE.get(str(target_uuid))
    if rating is None:
        raise HTTPException(status_code=404, detail="rating_not_found")
    return rating


@router.post("/ratings/{target_uuid}/refresh", response_model=RatingRecord)
def refresh_rating(
    target_uuid: UUID,
    repository=Depends(get_repository),
    vault_root: Path = Depends(get_vault_root),
) -> RatingRecord:
    target_entity = repository.get_entity(target_uuid) if hasattr(repository, "get_entity") else None
    if target_entity is None:
        raise HTTPException(status_code=404, detail="rating_target_not_found")

    record = build_rating_record(
        target_entity,
        reports=_reports_for_target(repository, target_uuid),
        relationships=_relationships_for_target(repository, target_uuid),
    )
    write_rating_markdown(record, vault_root)
    now = datetime.now(timezone.utc)
    if hasattr(repository, "upsert_entity"):
        repository.upsert_entity(
            KnowledgeEntity(
                uuid=record.rating_uuid,
                entity_type=EntityType.rating,
                slug=Path(record.vault_path).stem,
                title=f"{record.target_title} evidence history",
                vault_path=record.vault_path,
                created_at=now,
                updated_at=now,
            )
        )
    _RATING_STORE[str(target_uuid)] = record
    return record
