from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.ground_truth import get_repository, get_vault_root
from app.api.knowledge_ratings import clear_ratings_for_tests
from app.knowledge.ratings import build_rating_record, write_rating_markdown
from app.main import app
from app.schemas.ratings import RatingBadge, RatingConfidence

TARGET_UUID = UUID("00000000-0000-4000-8000-000000000010")
REPORT_UUID = UUID("00000000-0000-4000-8000-000000000011")
EVIDENCE_UUID = UUID("00000000-0000-4000-8000-000000000012")
RELATIONSHIP_UUID = UUID("00000000-0000-4000-8000-000000000013")

client = TestClient(app)


class FakeRepository:
    def __init__(self, reports=None) -> None:
        self.reports = reports or []
        self.entities = []

    def get_entity(self, target_uuid):
        if target_uuid == TARGET_UUID:
            return {
                "uuid": str(TARGET_UUID),
                "entity_type": "paper",
                "title": "Attention Is All You Need",
                "vault_path": "wiki/papers/attention-is-all-you-need.md",
            }
        return None

    def list_reports_for_rating(self, target_uuid):
        return self.reports

    def list_relationships(self, source_uuid=None, target_uuid=None):
        return [
            {
                "uuid": str(RELATIONSHIP_UUID),
                "relationship_type": "supports",
                "source_uuid": str(TARGET_UUID),
                "target_uuid": str(uuid4()),
                "provenance": "report-v1",
            }
        ]

    def upsert_entity(self, entity):
        self.entities.append(entity)


def setup_function(_function):
    clear_ratings_for_tests()
    app.dependency_overrides.clear()


def _target():
    return {
        "uuid": str(TARGET_UUID),
        "entity_type": "paper",
        "title": "Attention Is All You Need",
    }


def _report(label_counts):
    return {
        "report_uuid": str(REPORT_UUID),
        "label_counts": label_counts,
        "cited_evidence_uuids": [str(EVIDENCE_UUID)],
        "markdown_path": "vault/wiki/reports/report-v1.md",
    }


def test_zero_evidence_gives_insufficient_history():
    record = build_rating_record(_target(), [], [])

    assert record.badge == RatingBadge.insufficient_history
    assert record.evidence_count == 0
    assert record.confidence_level == RatingConfidence.low


def test_fewer_than_ten_evidence_items_gives_limited_experimental():
    record = build_rating_record(_target(), [_report({"supported": 3})], [])

    assert record.badge == RatingBadge.limited_evidence
    assert record.experimental is True


def test_mixed_labels_give_mixed_evidence_history():
    record = build_rating_record(_target(), [_report({"supported": 7, "mixed": 3})], [])

    assert record.badge == RatingBadge.mixed_evidence_history
    assert record.experimental is False


def test_supported_history_can_give_strong_evidence_history():
    record = build_rating_record(_target(), [_report({"supported": 9, "contradicted": 1})], [])

    assert record.badge == RatingBadge.strong_evidence_history
    assert record.confidence_level == RatingConfidence.high


def test_rating_markdown_contains_required_basis_sections(tmp_path):
    record = build_rating_record(_target(), [_report({"supported": 9, "contradicted": 1})], [])

    path = write_rating_markdown(record, tmp_path / "vault")
    markdown = path.read_text(encoding="utf-8")

    assert "## Evidence count" in markdown
    assert "## Label distribution" in markdown
    assert "## Source basis" in markdown
    assert "## Confidence level" in markdown
    assert "## Report versions" in markdown


def test_refresh_rating_api_returns_basis_and_upserts_rating_entity(tmp_path):
    repository = FakeRepository(reports=[_report({"supported": 9, "contradicted": 1})])
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_vault_root] = lambda: tmp_path / "vault"

    refresh_response = client.post(f"/knowledge/ratings/{TARGET_UUID}/refresh")
    fetch_response = client.get(f"/knowledge/ratings/{TARGET_UUID}")

    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert payload["badge"] == "strong evidence history"
    assert payload["source_basis"] == ["vault/wiki/reports/report-v1.md"]
    assert payload["confidence_level"] == "high"
    assert fetch_response.json()["target_uuid"] == str(TARGET_UUID)
    assert repository.entities[0].entity_type == "rating"


def test_rating_modules_avoid_forbidden_copy():
    forbidden = [
        "truth score",
        "trust score",
        "reputation score",
        "reliable creator",
        "unreliable creator",
    ]
    module_paths = [
        "app/knowledge/ratings.py",
        "app/api/knowledge_ratings.py",
        "app/schemas/ratings.py",
    ]
    for relative_path in module_paths:
        text = (Path(__file__).parent.parent / relative_path).read_text(encoding="utf-8")
        assert not any(phrase in text for phrase in forbidden)
