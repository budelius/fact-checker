import re
from datetime import UTC, datetime
from uuid import uuid4

from app.contracts.vault import expected_wiki_path
from app.schemas.claims import ExtractedClaim
from app.schemas.entities import EntityType, ExternalId, KnowledgeEntity
from app.schemas.ingestion import IngestionJob, ScreenshotArtifact, TranscriptArtifact
from app.schemas.relationships import KnowledgeRelationship, RelationshipType


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def _now() -> datetime:
    return datetime.now(UTC)


def _entity(
    uuid,
    entity_type: EntityType,
    slug: str,
    title: str,
    vault_folder: str,
    aliases: list[str] | None = None,
    external_ids: list[ExternalId] | None = None,
) -> KnowledgeEntity:
    now = _now()
    return KnowledgeEntity(
        uuid=uuid,
        entity_type=entity_type,
        slug=slug,
        title=title,
        vault_path=expected_wiki_path(vault_folder, slug),
        aliases=aliases or [],
        external_ids=external_ids or [],
        created_at=now,
        updated_at=now,
    )


def build_video_entity(job: IngestionJob) -> KnowledgeEntity:
    slug = slugify(job.source_url.replace("https://", "").replace("http://", ""))
    return _entity(
        uuid=job.video_uuid or uuid4(),
        entity_type=EntityType.video,
        slug=slug,
        title=f"Video source {slug}",
        vault_folder="videos",
        aliases=[job.source_url],
        external_ids=[ExternalId(provider=job.source_kind.value, value=job.source_url)],
    )


def build_transcript_entity(transcript: TranscriptArtifact, slug: str) -> KnowledgeEntity:
    return _entity(
        uuid=transcript.transcript_uuid,
        entity_type=EntityType.transcript,
        slug=slug,
        title=f"Transcript {slug}",
        vault_folder="transcripts",
        external_ids=[
            ExternalId(provider=transcript.provenance.method.value, value=transcript.provenance.source_url)
        ],
    )


def build_screenshot_entity(screenshot: ScreenshotArtifact, slug: str) -> KnowledgeEntity:
    return _entity(
        uuid=screenshot.screenshot_uuid,
        entity_type=EntityType.screenshot,
        slug=slug,
        title=f"Screenshot {slug}",
        vault_folder="screenshots",
        aliases=[screenshot.vault_path],
    )


def build_claim_entity(claim: ExtractedClaim, slug: str) -> KnowledgeEntity:
    return _entity(
        uuid=claim.uuid,
        entity_type=EntityType.claim,
        slug=slug,
        title=claim.claim_text[:80],
        vault_folder="claims",
        aliases=[claim.transcript_excerpt],
        external_ids=[ExternalId(provider="evidence_status", value=claim.evidence_status.value)],
    )


def build_claim_relationships(claim: ExtractedClaim) -> list[KnowledgeRelationship]:
    now = _now()
    targets = [claim.source_video_uuid, claim.source_transcript_uuid, *claim.screenshot_uuids]
    return [
        KnowledgeRelationship(
            uuid=uuid4(),
            relationship_type=RelationshipType.derived_from,
            source_uuid=claim.uuid,
            target_uuid=target_uuid,
            provenance="phase-2-ingestion",
            created_at=now,
        )
        for target_uuid in targets
    ]


def persist_ingestion_result(
    repository,
    job: IngestionJob,
    transcript: TranscriptArtifact | None,
    screenshots: list[ScreenshotArtifact],
    claims: list[ExtractedClaim],
) -> dict[str, int]:
    entity_count = 0
    relationship_count = 0

    repository.upsert_entity(build_video_entity(job))
    entity_count += 1

    if transcript is not None:
        repository.upsert_entity(build_transcript_entity(transcript, slugify(f"{job.source_url}-transcript")))
        entity_count += 1

    for index, screenshot in enumerate(screenshots, start=1):
        repository.upsert_entity(
            build_screenshot_entity(screenshot, slugify(f"{job.source_url}-screenshot-{index}"))
        )
        entity_count += 1

    for index, claim in enumerate(claims, start=1):
        repository.upsert_entity(build_claim_entity(claim, slugify(f"{job.source_url}-claim-{index}")))
        entity_count += 1
        for relationship in build_claim_relationships(claim):
            repository.upsert_relationship(relationship)
            relationship_count += 1

    return {"entities": entity_count, "relationships": relationship_count}
