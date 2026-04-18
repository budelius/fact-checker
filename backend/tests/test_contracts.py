from app.contracts.store_sync import QDRANT_REQUIRED_PAYLOAD_KEYS, build_trace_keys
from app.contracts.vault import (
    REQUIRED_FRONTMATTER_KEYS,
    VAULT_WIKI_ENTITY_FOLDERS,
    expected_wiki_path,
)


def test_vault_folders_match_contract():
    assert VAULT_WIKI_ENTITY_FOLDERS == (
        "videos",
        "creators",
        "claims",
        "papers",
        "authors",
        "sources",
        "evidence",
        "reports",
        "topics",
    )


def test_required_frontmatter_includes_uuid():
    assert "uuid" in REQUIRED_FRONTMATTER_KEYS
    assert "relationships" in REQUIRED_FRONTMATTER_KEYS


def test_qdrant_payload_keys_include_vault_path():
    assert "vault_path" in QDRANT_REQUIRED_PAYLOAD_KEYS
    assert "chunk_id" in QDRANT_REQUIRED_PAYLOAD_KEYS


def test_expected_wiki_path():
    assert (
        expected_wiki_path("claims", "transformer-attention-scaling")
        == "vault/wiki/claims/transformer-attention-scaling.md"
    )


def test_build_trace_keys():
    assert build_trace_keys(
        uuid="00000000-0000-4000-8000-000000000001",
        entity_type="paper",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
    ) == {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "entity_type": "paper",
        "vault_path": "vault/wiki/papers/attention-is-all-you-need.md",
    }
