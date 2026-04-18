import pytest

from app.contracts.logging import (
    PIPELINE_EVENT_TYPES,
    REQUIRED_PIPELINE_LOG_KEYS,
    build_pipeline_log_event,
)
from app.contracts.store_sync import QDRANT_REQUIRED_PAYLOAD_KEYS, build_trace_keys
from app.contracts.vault import (
    REQUIRED_FRONTMATTER_KEYS,
    VAULT_RAW_ARTIFACT_FOLDERS,
    VAULT_WIKI_ENTITY_FOLDERS,
    expected_raw_artifact_path,
    expected_wiki_path,
)


def test_vault_folders_match_contract():
    assert VAULT_WIKI_ENTITY_FOLDERS == (
        "videos",
        "creators",
        "transcripts",
        "screenshots",
        "claims",
        "papers",
        "authors",
        "sources",
        "evidence",
        "reports",
        "topics",
    )

    assert VAULT_RAW_ARTIFACT_FOLDERS == ("videos", "transcripts", "screenshots", "papers")


def test_required_frontmatter_includes_uuid():
    assert "uuid" in REQUIRED_FRONTMATTER_KEYS
    assert "relationships" in REQUIRED_FRONTMATTER_KEYS


def test_qdrant_payload_keys_include_vault_path():
    assert "vault_path" in QDRANT_REQUIRED_PAYLOAD_KEYS
    assert "chunk_id" in QDRANT_REQUIRED_PAYLOAD_KEYS
    assert "source" in QDRANT_REQUIRED_PAYLOAD_KEYS
    assert "source_date" in QDRANT_REQUIRED_PAYLOAD_KEYS
    assert "relationship_uuids" in QDRANT_REQUIRED_PAYLOAD_KEYS


def test_expected_wiki_path():
    assert (
        expected_wiki_path("claims", "transformer-attention-scaling")
        == "vault/wiki/claims/transformer-attention-scaling.md"
    )


def test_raw_artifact_path_for_screenshot():
    assert (
        expected_raw_artifact_path("screenshots", "attention-slide-001", ".png")
        == "vault/raw/screenshots/attention-slide-001.png"
    )


def test_raw_artifact_path_for_paper_pdf():
    assert (
        expected_raw_artifact_path("papers", "attention-is-all-you-need", ".pdf")
        == "vault/raw/papers/attention-is-all-you-need.pdf"
    )


def test_build_trace_keys():
    assert build_trace_keys(
        uuid="00000000-0000-4000-8000-000000000001",
        entity_type="paper",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        chunk_id="abstract-0001",
        source="arxiv:1706.03762",
        source_date="2017-06-12",
        relationship_uuids=["00000000-0000-4000-8000-000000000003"],
    ) == {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "entity_type": "paper",
        "vault_path": "vault/wiki/papers/attention-is-all-you-need.md",
        "chunk_id": "abstract-0001",
        "source": "arxiv:1706.03762",
        "source_date": "2017-06-12",
        "relationship_uuids": ["00000000-0000-4000-8000-000000000003"],
    }


def test_pipeline_logging_contract():
    assert "indexing" in PIPELINE_EVENT_TYPES
    assert "graph_write" in PIPELINE_EVENT_TYPES
    assert "source_discovery" in PIPELINE_EVENT_TYPES
    assert "paper_processing" in PIPELINE_EVENT_TYPES
    assert "summarization" in PIPELINE_EVENT_TYPES
    assert "event_type" in REQUIRED_PIPELINE_LOG_KEYS
    assert "job_uuid" in REQUIRED_PIPELINE_LOG_KEYS

    event = build_pipeline_log_event(
        event_type="indexing",
        job_uuid="00000000-0000-4000-8000-000000000010",
        stage="qdrant_upsert",
        status="succeeded",
        message="Indexed chunk",
        created_at="2026-04-18T00:00:00Z",
        entity_uuid="00000000-0000-4000-8000-000000000001",
    )

    assert event["event_type"] == "indexing"
    assert event["entity_uuid"] == "00000000-0000-4000-8000-000000000001"

    source_discovery_event = build_pipeline_log_event(
        event_type="source_discovery",
        job_uuid="00000000-0000-4000-8000-000000000010",
        stage="merge_candidates",
        status="succeeded",
        message="Merged paper candidates",
        created_at="2026-04-18T00:00:00Z",
    )

    assert source_discovery_event["stage"] == "merge_candidates"


def test_pipeline_logging_rejects_unknown_event_type():
    with pytest.raises(ValueError):
        build_pipeline_log_event(
            event_type="unknown",
            job_uuid="00000000-0000-4000-8000-000000000010",
            stage="qdrant_upsert",
            status="succeeded",
            message="Indexed chunk",
            created_at="2026-04-18T00:00:00Z",
        )
