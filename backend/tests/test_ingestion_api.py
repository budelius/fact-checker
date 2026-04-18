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


def test_submit_supported_tiktok_returns_job_uuid(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)
    monkeypatch.setenv("TIKTOK_MEDIA_DOWNLOAD_ENABLED", "true")

    async def fake_fetch_public_metadata(_url):
        return {
            "id": "1234567890",
            "title": "Attention paper explained",
            "creator_alias": "fixture_creator",
            "description": "arXiv:1706.03762",
        }

    async def fake_extract_subtitle_file(_url, output_dir):
        subtitle_file = output_dir / "subs.en.vtt"
        subtitle_file.write_text(
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.500\n"
            "A paper says transformers scale well.\n\n"
            "00:00:04.000 --> 00:00:06.000\n"
            "The source is arXiv:1706.03762.\n",
            encoding="utf-8",
        )
        return subtitle_file

    async def fake_extract_thumbnail_file(_url, output_dir):
        thumbnail_file = output_dir / "thumbnail.image"
        thumbnail_file.write_bytes(b"\xff\xd8\xfffake-thumbnail")
        return thumbnail_file

    async def fake_download_video_file(_url, output_dir, _max_video_mb):
        video_file = output_dir / "video.mp4"
        video_file.write_bytes(b"fake-video")
        return video_file

    async def fake_extract_frame_with_ffmpeg(_video_file, output_dir, _slug, timestamp_seconds):
        assert timestamp_seconds == 1.0
        frame_file = output_dir / "source-clue-frame.jpg"
        frame_file.write_bytes(b"\xff\xd8\xfffake-ffmpeg-frame")
        return frame_file

    monkeypatch.setattr("app.api.ingestion.fetch_public_metadata", fake_fetch_public_metadata)
    monkeypatch.setattr("app.api.ingestion.extract_subtitle_file", fake_extract_subtitle_file)
    monkeypatch.setattr("app.api.ingestion.extract_thumbnail_file", fake_extract_thumbnail_file)
    monkeypatch.setattr("app.api.ingestion.download_video_file", fake_download_video_file)
    monkeypatch.setattr("app.api.ingestion.extract_frame_with_ffmpeg", fake_extract_frame_with_ffmpeg)

    response = client.post(
        "/ingestion/tiktok",
        json={"url": "https://www.tiktok.com/@fixture/video/1234567890"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert UUID(payload["job_uuid"])
    assert payload["status"] == "succeeded"
    assert "ready for paper discovery" in payload["current_operation"]
    assert payload["public_metadata"]["external_video_id"] == "1234567890"
    assert payload["transcript_artifact"]["provenance"]["method"] == "subtitle_file"
    assert payload["screenshots"][0]["asset_url"].startswith(
        "/ingestion/artifacts/raw/screenshots/"
    )
    assert payload["screenshots"][0]["asset_url"].endswith(".jpg")
    assert payload["screenshots"][0]["source_clue"] is True
    assert payload["claims"][0]["evidence_status"] == "pending"
    metadata_artifact = next(
        artifact for artifact in payload["artifacts"] if artifact["artifact_type"] == "public_metadata"
    )
    assert metadata_artifact["status"] == "succeeded"

    asset_response = client.get(payload["screenshots"][0]["asset_url"])
    assert asset_response.status_code == 200
    assert asset_response.content == b"\xff\xd8\xfffake-ffmpeg-frame"


def test_submit_unsupported_tiktok_url_returns_400():
    response = client.post("/ingestion/tiktok", json={"url": "https://example.com/video/1"})

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_tiktok_url"


def test_fixture_transcript_flow_completes_with_research_basis():
    response = client.post(
        "/ingestion/fixtures/transcript",
        json={
            "source_url": "https://www.tiktok.com/@fixture/video/1234567890",
            "title": "Attention paper explained",
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
    assert payload["status"] == "succeeded"
    assert payload["research_basis"]["candidate_count"] > 0
    assert payload["claims"][0]["evidence_status"] == "pending"
    assert "ready for paper discovery" in payload["current_operation"]

    fetched = client.get(f"/ingestion/jobs/{payload['job_uuid']}")
    assert fetched.status_code == 200
    assert fetched.json()["job_uuid"] == payload["job_uuid"]


def test_missing_job_returns_404():
    response = client.get("/ingestion/jobs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["detail"] == "ingestion_job_not_found"


def test_upload_video_returns_local_media_artifact(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        files={"file": ("fixture.mp4", b"fake-video", "video/mp4")},
        data={"transcript": "A study claims LLM agents improve benchmark performance. arXiv:1706.03762"},
    )

    assert response.status_code == 200
    payload = response.json()
    media_artifact = next(
        artifact for artifact in payload["artifacts"] if artifact["artifact_type"] == "media_retrieval"
    )
    assert media_artifact["details"]["vault_path"].startswith("vault/raw/videos/")
    assert media_artifact["details"]["third_party_upload"] is False
    assert payload["status"] == "succeeded"


def test_unsupported_video_upload_type_returns_400(monkeypatch, tmp_path):
    _use_temp_vault(monkeypatch, tmp_path)

    response = client.post(
        "/ingestion/videos/upload",
        files={"file": ("fixture.txt", b"not-video", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "unsupported_upload_type"
