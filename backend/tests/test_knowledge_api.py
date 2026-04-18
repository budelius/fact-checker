from uuid import UUID

from fastapi.testclient import TestClient

from app.api.ground_truth import get_repository, get_vault_root
from app.knowledge.annotations import clear_annotations_for_tests
from app.main import app

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
CLAIM_UUID = UUID("00000000-0000-4000-8000-000000000002")

client = TestClient(app)


class FakeRepository:
    def __init__(self) -> None:
        self.annotations: list[dict] = []

    def upsert_annotation(self, annotation: dict) -> None:
        self.annotations.append(annotation)

    def list_annotations(self, target_entity_uuid: UUID) -> list[dict]:
        return [
            annotation
            for annotation in self.annotations
            if annotation["target_entity_uuid"] == str(target_entity_uuid)
        ]


def setup_function(_function):
    clear_annotations_for_tests()
    app.dependency_overrides.clear()


def _write_note(path, frontmatter: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter.strip()}\n---\n{body.strip()}\n", encoding="utf-8")


def _make_vault(tmp_path):
    vault = tmp_path / "vault"
    _write_note(
        vault / "wiki" / "papers" / "attention-is-all-you-need.md",
        f"""
uuid: {PAPER_UUID}
entity_type: paper
slug: attention-is-all-you-need
title: Attention Is All You Need
aliases: []
external_ids: []
relationships:
  - relationship_type: supports
    source_uuid: {PAPER_UUID}
    target_uuid: {CLAIM_UUID}
    provenance: report-v1
created_at: 2026-04-18T00:00:00Z
updated_at: 2026-04-18T00:00:00Z
""",
        """
# Summary

The paper supports [[claims/transformer-attention-scaling]].
""",
    )
    return vault


def _override_dependencies(tmp_path, repository):
    vault = _make_vault(tmp_path)
    app.dependency_overrides[get_vault_root] = lambda: vault
    app.dependency_overrides[get_repository] = lambda: repository
    return vault


def test_knowledge_sections_and_note_list(tmp_path):
    _override_dependencies(tmp_path, FakeRepository())

    sections = client.get("/knowledge/sections")
    notes = client.get("/knowledge/notes?entity_type=paper")

    assert sections.status_code == 200
    assert notes.status_code == 200
    assert sections.json()[0]["entity_type"] == "paper"
    assert notes.json()[0]["uuid"] == str(PAPER_UUID)


def test_knowledge_note_detail_keeps_body_and_frontmatter_separate(tmp_path):
    _override_dependencies(tmp_path, FakeRepository())

    response = client.get(f"/knowledge/notes/{PAPER_UUID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["body_markdown"].startswith("# Summary")
    assert payload["frontmatter"]["uuid"] == str(PAPER_UUID)
    assert payload["relationships"][0]["relationship_type"] == "supports"
    assert payload["annotations"] == []


def test_create_annotation_returns_separate_record(tmp_path):
    repository = FakeRepository()
    _override_dependencies(tmp_path, repository)

    response = client.post(
        f"/knowledge/notes/{PAPER_UUID}/annotations",
        json={"body": "This is a separate user note."},
    )
    detail = client.get(f"/knowledge/notes/{PAPER_UUID}")

    assert response.status_code == 200
    assert response.json()["author"] == "user"
    assert detail.json()["annotations"][0]["body"] == "This is a separate user note."
    assert "This is a separate user note." not in detail.json()["body_markdown"]
