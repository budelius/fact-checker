from uuid import UUID

from fastapi.testclient import TestClient

from app.api.ground_truth import get_qdrant_repository, get_repository, get_vault_root
from app.knowledge.consistency import check_knowledge_consistency
from app.main import app

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
CLAIM_UUID = UUID("00000000-0000-4000-8000-000000000002")
ORPHAN_UUID = UUID("00000000-0000-4000-8000-000000000099")

client = TestClient(app)


class FakeRepository:
    def __init__(self, include_entity: bool = True) -> None:
        self.include_entity = include_entity

    def list_entities(self, entity_type=None):
        if not self.include_entity:
            return []
        return [
            {
                "uuid": str(PAPER_UUID),
                "entity_type": "paper",
                "title": "Attention Is All You Need",
                "vault_path": "wiki/papers/attention-is-all-you-need.md",
            }
        ]

    def list_relationships(self, source_uuid=None, target_uuid=None):
        return [
            {
                "uuid": "00000000-0000-4000-8000-000000000004",
                "relationship_type": "supports",
                "source_uuid": str(PAPER_UUID),
                "target_uuid": str(CLAIM_UUID),
                "provenance": "report-v1",
            }
        ]


class FakeQdrantRepository:
    def __init__(self, payloads=None) -> None:
        self.payloads = payloads or []

    def scroll_payloads(self):
        return self.payloads


def setup_function(_function):
    app.dependency_overrides.clear()


def _write_note(path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
uuid: {PAPER_UUID}
entity_type: paper
slug: attention-is-all-you-need
title: Attention Is All You Need
aliases: []
external_ids: []
relationships: []
created_at: 2026-04-18T00:00:00Z
updated_at: 2026-04-18T00:00:00Z
---
# Summary

The paper supports [[claims/transformer-attention-scaling]].
""",
        encoding="utf-8",
    )


def test_consistency_reports_drift_for_missing_qdrant_payload(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")

    summary = check_knowledge_consistency(vault, FakeRepository(), FakeQdrantRepository())

    assert summary.missing_qdrant_payloads == 1
    assert any(issue.status == "drift" for issue in summary.issues)
    assert summary.broken_relationships == 1


def test_consistency_reports_broken_for_missing_canonical_record(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")

    summary = check_knowledge_consistency(vault, FakeRepository(False), FakeQdrantRepository())

    assert summary.missing_mongo_records == 1
    assert any(issue.status == "broken" for issue in summary.issues)


def test_consistency_reports_orphan_vectors(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")

    summary = check_knowledge_consistency(
        vault,
        FakeRepository(),
        FakeQdrantRepository(
            [{"uuid": str(ORPHAN_UUID), "vault_path": "wiki/papers/orphan.md"}]
        ),
    )

    assert summary.orphan_vectors == 1


def test_consistency_api_returns_summary(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")
    app.dependency_overrides[get_vault_root] = lambda: vault
    app.dependency_overrides[get_repository] = lambda: FakeRepository()
    app.dependency_overrides[get_qdrant_repository] = lambda: FakeQdrantRepository()

    response = client.get("/knowledge/consistency")

    assert response.status_code == 200
    payload = response.json()
    assert payload["checked_notes"] == 1
    assert payload["missing_qdrant_payloads"] == 1
