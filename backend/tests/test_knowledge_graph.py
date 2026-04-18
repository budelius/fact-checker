from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from app.api.ground_truth import get_repository
from app.knowledge.graph import build_entity_graph
from app.main import app

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
CLAIM_UUID = UUID("00000000-0000-4000-8000-000000000002")
RELATIONSHIP_UUID = UUID("00000000-0000-4000-8000-000000000004")

client = TestClient(app)


class FakeRepository:
    def list_entities(self, entity_type=None):
        return [
            {
                "uuid": str(PAPER_UUID),
                "entity_type": "paper",
                "title": "Attention Is All You Need",
                "vault_path": "wiki/papers/attention-is-all-you-need.md",
            },
            {
                "uuid": str(CLAIM_UUID),
                "entity_type": "claim",
                "title": "Transformer attention scaling",
                "vault_path": "wiki/claims/transformer-attention-scaling.md",
            },
        ]

    def list_relationships(self, source_uuid=None, target_uuid=None):
        return [
            {
                "uuid": str(RELATIONSHIP_UUID),
                "relationship_type": "supports",
                "source_uuid": str(PAPER_UUID),
                "target_uuid": str(CLAIM_UUID),
                "provenance": "report-v1",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]


def setup_function(_function):
    app.dependency_overrides.clear()


def test_build_entity_graph_returns_nodes_edges_and_clusters():
    graph = build_entity_graph(PAPER_UUID, FakeRepository())

    assert graph.selected_uuid == PAPER_UUID
    assert {node.uuid for node in graph.nodes} == {PAPER_UUID, CLAIM_UUID}
    assert graph.edges[0].relationship_type == "supports"
    assert graph.edges[0].direction == "outgoing"
    assert graph.important_nodes
    assert "paper" in graph.clusters


def test_graph_api_returns_selected_entity_graph():
    app.dependency_overrides[get_repository] = lambda: FakeRepository()

    response = client.get(f"/knowledge/graph/{PAPER_UUID}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_uuid"] == str(PAPER_UUID)
    assert payload["edges"][0]["relationship_type"] == "supports"
    assert payload["nodes"][0]["uuid"]
