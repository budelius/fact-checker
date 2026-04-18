from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid5

from app.contracts.vault import expected_wiki_path
from app.ground_truth.markdown import build_paper_markdown, paper_slug
from app.ingestion.persistence import slugify
from app.schemas.entities import EntityType, ExternalId, KnowledgeEntity
from app.schemas.ground_truth import (
    CandidateStatus,
    PaperAuthor,
    PaperChunk,
    PaperMetadata,
    PaperSummary,
    SourceDecision,
)
from app.schemas.relationships import KnowledgeRelationship, RelationshipType


def _now() -> datetime:
    return datetime.now(UTC)


def _external_ids(metadata: PaperMetadata) -> list[ExternalId]:
    return [ExternalId(provider=item.provider, value=item.value) for item in metadata.external_ids]


def _entity(uuid: UUID, entity_type: EntityType, slug: str, title: str, vault_path: str) -> KnowledgeEntity:
    now = _now()
    return KnowledgeEntity(
        uuid=uuid,
        entity_type=entity_type,
        slug=slug,
        title=title,
        vault_path=vault_path,
        created_at=now,
        updated_at=now,
    )


def _author_uuid(paper_uuid: UUID, author: PaperAuthor) -> UUID:
    return uuid5(paper_uuid, f"author:{author.name.lower()}")


def _relationship(
    relationship_type: RelationshipType,
    source_uuid: UUID,
    target_uuid: UUID,
    provenance: str,
) -> KnowledgeRelationship:
    return KnowledgeRelationship(
        uuid=uuid5(source_uuid, f"{relationship_type.value}:{target_uuid}:{provenance}"),
        relationship_type=relationship_type,
        source_uuid=source_uuid,
        target_uuid=target_uuid,
        provenance=provenance,
        created_at=_now(),
    )


def persist_paper_knowledge(
    repository,
    vault_root: Path,
    metadata: PaperMetadata,
    summary: PaperSummary | None,
    chunks: list[PaperChunk],
    decisions: list[SourceDecision],
) -> dict[str, int]:
    slug = paper_slug(metadata)
    metadata.vault_path = expected_wiki_path("papers", slug)
    selected_claim_uuids = [
        decision.claim_uuid
        for decision in decisions
        if decision.status == CandidateStatus.selected_ground_truth and decision.claim_uuid is not None
    ]
    markdown = build_paper_markdown(metadata, summary, selected_claim_uuids, decisions)
    note_path = vault_root / "wiki" / "papers" / f"{slug}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(markdown, encoding="utf-8")

    entity_count = 0
    relationship_count = 0
    paper_entity = _entity(metadata.uuid, EntityType.paper, slug, metadata.title, metadata.vault_path)
    paper_entity.external_ids = _external_ids(metadata)
    paper_entity.aliases = [item.value for item in metadata.external_ids]
    repository.upsert_entity(paper_entity)
    entity_count += 1

    for author in metadata.authors:
        author_slug = slugify(author.name)
        author_uuid = _author_uuid(metadata.uuid, author)
        author_entity = _entity(
            author_uuid,
            EntityType.author,
            author_slug,
            author.name,
            expected_wiki_path("authors", author_slug),
        )
        author_entity.external_ids = [
            ExternalId(provider=item.provider, value=item.value) for item in author.external_ids
        ]
        repository.upsert_entity(author_entity)
        entity_count += 1
        repository.upsert_relationship(
            _relationship(RelationshipType.authored_by, metadata.uuid, author_uuid, "phase-3-ground-truth")
        )
        relationship_count += 1

    for chunk in chunks:
        chunk_slug = slugify(f"{slug}-{chunk.chunk_id}")
        repository.upsert_entity(
            _entity(
                chunk.uuid,
                EntityType.evidence,
                chunk_slug,
                f"{metadata.title} {chunk.chunk_id}",
                expected_wiki_path("evidence", chunk_slug),
            )
        )
        entity_count += 1
        repository.upsert_relationship(
            _relationship(RelationshipType.derived_from, chunk.uuid, metadata.uuid, "phase-3-ground-truth")
        )
        relationship_count += 1

    for claim_uuid in selected_claim_uuids:
        repository.upsert_relationship(
            _relationship(RelationshipType.cites, claim_uuid, metadata.uuid, "phase-3-ground-truth")
        )
        relationship_count += 1

    return {"entities": entity_count, "relationships": relationship_count, "markdown_files": 1}
