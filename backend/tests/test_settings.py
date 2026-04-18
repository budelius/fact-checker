from fastapi.testclient import TestClient

from app.main import app
from app.settings import Settings


def test_settings_from_environment(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", "../vault")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = Settings()

    assert settings.mongodb_uri == "mongodb://example"
    assert settings.mongodb_database == "fact_checker"
    assert settings.qdrant_url == "http://localhost:6333"
    assert settings.qdrant_collection_knowledge == "fact_checker_knowledge"
    assert settings.vault_root == "../vault"
    assert settings.log_level == "INFO"


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
