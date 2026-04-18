from fastapi.testclient import TestClient

from app.main import app
from app.settings import Settings


def set_required_settings(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", "../vault")
    monkeypatch.setenv("LOG_LEVEL", "INFO")


def test_settings_from_environment(monkeypatch):
    set_required_settings(monkeypatch)

    settings = Settings()

    assert settings.mongodb_uri == "mongodb://example"
    assert settings.mongodb_database == "fact_checker"
    assert settings.qdrant_url == "http://localhost:6333"
    assert settings.qdrant_collection_knowledge == "fact_checker_knowledge"
    assert settings.vault_root == "../vault"
    assert settings.log_level == "INFO"


def test_ground_truth_settings_defaults(monkeypatch):
    set_required_settings(monkeypatch)

    settings = Settings()

    assert settings.openai_discovery_model == "gpt-5.4-mini"
    assert settings.openai_summary_model == "gpt-5.4-mini"
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.openai_embedding_dimensions is None
    assert settings.openalex_email is None
    assert settings.semantic_scholar_api_key is None
    assert settings.ground_truth_max_results_per_provider == 10
    assert settings.paper_download_enabled is True
    assert settings.paper_max_pdf_mb == 40
    assert settings.paper_request_timeout_seconds == 20.0


def test_ground_truth_settings_from_env(monkeypatch):
    set_required_settings(monkeypatch)
    monkeypatch.setenv("OPENAI_DISCOVERY_MODEL", "gpt-test")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "embedding-test")
    monkeypatch.setenv("OPENALEX_EMAIL", "research@example.com")
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "s2-key")
    monkeypatch.setenv("PAPER_DOWNLOAD_ENABLED", "false")

    settings = Settings()

    assert settings.openai_discovery_model == "gpt-test"
    assert settings.openai_embedding_model == "embedding-test"
    assert settings.openalex_email == "research@example.com"
    assert settings.semantic_scholar_api_key == "s2-key"
    assert settings.paper_download_enabled is False


def test_contracts_endpoint():
    client = TestClient(app)

    response = client.get("/contracts")

    assert response.status_code == 200
    assert response.json() == {
        "identity": "uuid",
        "metadata_store": "mongodb",
        "vector_store": "qdrant",
        "vault": "markdown",
    }
