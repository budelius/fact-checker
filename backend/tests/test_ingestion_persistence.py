from uuid import uuid4

from app.ingestion.jobs import create_ingestion_job
from app.ingestion.persistence import (
    build_claim_entity,
    build_claim_relationships,
    persist_ingestion_result,
    slugify,
)
from app.schemas.claims import ExtractedClaim
from app.schemas.ingestion import (
    ScreenshotArtifact,
    SourceKind,
    TranscriptArtifact,
    TranscriptProvenance,
    TranscriptRetrievalMethod,
)


class FakeRepository:
    def __init__(self):
        self.entities = []
        self.relationships = []

    def upsert_entity(self, entity):
        self.entities.append(entity)

    def upsert_relationship(self, relationship):
        self.relationships.append(relationship)


def _transcript(video_uuid) -> TranscriptArtifact:
    return TranscriptArtifact(
        video_uuid=video_uuid,
        provenance=TranscriptProvenance(
            method=TranscriptRetrievalMethod.fixture,
            source_url="https://www.tiktok.com/@fixture/video/1234567890",
        ),
        plain_text="A paper says attention works.",
    )


def test_persistence_uses_slug_only_vault_paths():
    assert slugify("Attention / Paper: 1706.03762") == "attention-paper-1706-03762"

    claim = ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt="paper says attention works",
        claim_text="Attention works.",
    )
    entity = build_claim_entity(claim, "attention-works")

    assert entity.vault_path == "vault/wiki/claims/attention-works.md"
    assert str(claim.uuid) not in entity.vault_path
    assert all(external.value not in {"supported", "contradicted", "mixed"} for external in entity.external_ids)


def test_persist_ingestion_result_upserts_entities_and_relationships():
    repository = FakeRepository()
    job = create_ingestion_job(
        "https://www.tiktok.com/@fixture/video/1234567890",
        source_kind=SourceKind.tiktok_url,
    )
    transcript = _transcript(job.video_uuid)
    screenshot = ScreenshotArtifact(
        video_uuid=job.video_uuid,
        timestamp_seconds=1.0,
        vault_path="vault/raw/screenshots/frame.png",
    )
    claim = ExtractedClaim(
        source_video_uuid=job.video_uuid,
        source_transcript_uuid=transcript.transcript_uuid,
        screenshot_uuids=[screenshot.screenshot_uuid],
        transcript_excerpt="paper says attention works",
        claim_text="Attention works.",
    )

    counts = persist_ingestion_result(repository, job, transcript, [screenshot], [claim])

    assert counts == {"entities": 4, "relationships": 3}
    assert len(repository.entities) == 4
    assert len(repository.relationships) == 3
    assert len(build_claim_relationships(claim)) == 3
