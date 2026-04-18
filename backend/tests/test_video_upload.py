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


def test_upload_video_returns_job_uuid_and_media_artifact(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        files={"file": ("fixture.mp4", b"not-a-real-video", "video/mp4")},
    )

    assert response.status_code == 200
    payload = response.json()
    media = next(
        artifact for artifact in payload["artifacts"] if artifact["artifact_type"] == "media_retrieval"
    )

    assert payload["job_uuid"]
    assert payload["source_kind"] == "uploaded_video"
    assert media["details"]["vault_path"].startswith("vault/raw/videos/")
    assert media["details"]["third_party_upload"] is False


def test_upload_video_with_transcript_runs_research_basis_flow(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        data={"transcript": "This paper mentions arXiv:1706.03762."},
        files={"file": ("fixture.webm", b"not-a-real-video", "video/webm")},
    )

    assert response.status_code == 200
    payload = response.json()
    research_basis = payload["research_basis"]

    assert payload["status"] == "succeeded"
    assert research_basis["candidate_count"] > 0
    assert payload["artifacts"][0]["details"]["vault_path"].startswith("vault/raw/videos/")


def test_upload_rejects_unsupported_type(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        files={"file": ("fixture.txt", b"text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_upload_type"
