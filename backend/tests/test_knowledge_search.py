from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.ground_truth import get_qdrant_repository, get_vault_root
from app.api.knowledge_search import get_settings
from app.knowledge.search import search_knowledge
from app.main import app
from app.repositories.qdrant import QdrantRepository

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
RELATIONSHIP_UUID = UUID("00000000-0000-4000-8000-000000000004")

client = TestClient(app)


class FakeEmbeddingProvider:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["attention"]
        return [[0.1, 0.2, 0.3]]


class FakeQdrantRepository:
    def __init__(self) -> None:
        self.entity_types = None

    def search_payloads(self, query_vector, limit=10, entity_types=None, source=None):
        self.entity_types = entity_types
        return [
            {
                "payload": {
                    "uuid": str(PAPER_UUID),
                    "entity_type": "paper",
                    "vault_path": "wiki/papers/attention-is-all-you-need.md",
                    "chunk_id": "summary",
                    "source": source or "paper_summary",
                    "relationship_uuids": [str(RELATIONSHIP_UUID)],
                },
                "score": 0.91,
            }
        ]


class FakeQdrantPoint:
    payload = {"uuid": str(PAPER_UUID), "entity_type": "paper"}
    score = 0.8


class FakeQdrantClient:
    def __init__(self) -> None:
        self.query_filter = None

    def collection_exists(self, _collection_name):
        return True

    def query_points(self, collection_name, query, query_filter=None, limit=10):
        self.query_filter = query_filter
        return SimpleNamespace(points=[FakeQdrantPoint()])


def setup_function(_function):
    app.dependency_overrides.clear()


def _write_note(path, body: str = "Scaled dot-product attention.") -> None:
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

{body}
""",
        encoding="utf-8",
    )


def test_qdrant_repository_search_payloads_uses_query_points_with_filters():
    qdrant = object.__new__(QdrantRepository)
    qdrant.client = FakeQdrantClient()
    qdrant.collection_name = "knowledge"

    results = qdrant.search_payloads([0.1], entity_types=["paper"], source="paper_summary")

    assert results[0]["payload"]["uuid"] == str(PAPER_UUID)
    assert results[0]["score"] == 0.8
    assert qdrant.client.query_filter is not None


def test_search_knowledge_uses_vector_payloads_with_traceability(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")
    qdrant = FakeQdrantRepository()

    results = search_knowledge(
        "attention",
        qdrant_repository=qdrant,
        embedding_provider=FakeEmbeddingProvider(),
        vault_root=vault,
        entity_types=["paper"],
    )

    assert qdrant.entity_types == ["paper"]
    assert results[0].uuid == PAPER_UUID
    assert results[0].entity_type == "paper"
    assert results[0].relationship_uuids == [RELATIONSHIP_UUID]
    assert results[0].vector_backed is True


def test_search_knowledge_fallback_matches_vault_text(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")

    results = search_knowledge(
        "scaled",
        qdrant_repository=None,
        embedding_provider=None,
        vault_root=vault,
    )

    assert results[0].uuid == PAPER_UUID
    assert results[0].source == "vault_fallback"
    assert results[0].vector_backed is False


def test_search_api_returns_fallback_results_and_accepts_entity_type_filter(tmp_path):
    vault = tmp_path / "vault"
    _write_note(vault / "wiki" / "papers" / "attention-is-all-you-need.md")
    app.dependency_overrides[get_vault_root] = lambda: vault
    app.dependency_overrides[get_qdrant_repository] = lambda: None
    app.dependency_overrides[get_settings] = lambda: SimpleNamespace(openai_api_key=None)

    response = client.get("/knowledge/search?q=attention&entity_type=paper")

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "attention"
    assert payload["count"] == 1
    assert payload["vector_backed"] is False
    assert payload["results"][0]["entity_type"] == "paper"
