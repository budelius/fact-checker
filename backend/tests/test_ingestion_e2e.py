from uuid import UUID

from fastapi.testclient import TestClient

from app.ingestion.jobs import clear_jobs_for_tests
from app.main import app
from app.settings import get_settings


client = TestClient(app)


def setup_function(_function):
    clear_jobs_for_tests()
    get_settings.cache_clear()


def _use_temp_vault(monkeypatch, tmp_path):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    get_settings.cache_clear()


def _stage_names(payload: dict) -> set[str]:
    return {stage["name"] for stage in payload["stages"]}


def _research_basis_artifact(payload: dict) -> dict:
    return next(artifact for artifact in payload["artifacts"] if artifact["artifact_type"] == "research_basis")


def test_fixture_transcript_e2e_research_backed_flow(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/fixtures/transcript",
        json={
            "source_url": "https://www.tiktok.com/@fixture/video/1234567890",
            "transcript": (
                "00:00:01.000 --> 00:00:03.500\n"
                "A paper says transformers scale well for sequence modeling.\n\n"
                "00:00:04.000 --> 00:00:05.500\n"
                "The source is arXiv:1706.03762."
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    fetched = client.get(f"/ingestion/jobs/{payload['job_uuid']}")

    assert fetched.status_code == 200
    assert UUID(payload["job_uuid"])
    assert payload["status"] == "succeeded"
    assert {"validate_url", "build_transcript", "triage_research_basis"}.issubset(
        _stage_names(payload)
    )
    assert _research_basis_artifact(payload)["details"]["candidate_count"] > 0
    assert payload["claims"][0]["evidence_status"] == "pending"


def test_uploaded_video_e2e_media_and_transcript_flow(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        data={"transcript": "A study discusses arXiv:1706.03762 and LLM benchmarks."},
        files={"file": ("fixture.mp4", b"not-a-real-video", "video/mp4")},
    )

    assert response.status_code == 200
    payload = response.json()
    fetched = client.get(f"/ingestion/jobs/{payload['job_uuid']}")
    media = next(
        artifact for artifact in payload["artifacts"] if artifact["artifact_type"] == "media_retrieval"
    )

    assert fetched.status_code == 200
    assert UUID(payload["job_uuid"])
    assert payload["status"] == "succeeded"
    assert {"validate_url", "build_transcript", "triage_research_basis"}.issubset(
        _stage_names(payload)
    )
    assert media["details"]["vault_path"].startswith("vault/raw/videos/")
    assert media["details"]["third_party_upload"] is False
    assert _research_basis_artifact(payload)["details"]["candidate_count"] > 0


def test_uploaded_video_without_transcript_marks_claim_provider_disabled(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        files={"file": ("fixture.mp4", b"not-a-real-video", "video/mp4")},
    )

    assert response.status_code == 200
    payload = response.json()
    extract_stage = next(stage for stage in payload["stages"] if stage["name"] == "extract_claims")

    assert extract_stage["status"] == "skipped"
    assert extract_stage["message"] == "claim_extraction_provider_disabled"
