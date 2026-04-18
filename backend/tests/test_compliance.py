from app.ingestion.compliance import decide_media_download
from app.settings import Settings


def _base_env(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", "../vault")
    monkeypatch.setenv("LOG_LEVEL", "INFO")


def test_media_download_default_denied(monkeypatch):
    _base_env(monkeypatch)

    settings = Settings()
    decision = decide_media_download(
        enabled=settings.tiktok_media_download_enabled,
        max_video_mb=settings.tiktok_max_video_mb,
    )

    assert decision.allowed is False
    assert decision.reason == "media_download_disabled"
    assert decision.download_attempted is False


def test_media_download_enabled_decision():
    decision = decide_media_download(enabled=True, max_video_mb=200)

    assert decision.allowed is True
    assert decision.reason == "media_download_enabled"
    assert decision.max_video_mb == 200
