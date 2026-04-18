from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.ground_truth import (
    clear_ground_truth_jobs_for_tests,
    get_pipeline,
    get_qdrant_repository,
    get_repository,
    get_vault_root,
)
from app.ingestion.jobs import clear_jobs_for_tests
from app.main import app
from app.schemas.ground_truth import CandidateStatus, GroundTruthJob, SourceDecision
from app.schemas.ingestion import JobLifecycleStatus
from app.settings import get_settings

client = TestClient(app)


def setup_function(_function):
    clear_jobs_for_tests()
    clear_ground_truth_jobs_for_tests()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


class FakePipeline:
    def run_from_ingestion_payload(self, ingestion_payload, repository, qdrant_repository, vault_root):
        claim_uuid = ingestion_payload["claims"][0]["uuid"]
        return GroundTruthJob(
            ingestion_job_uuid=ingestion_payload["job_uuid"],
            status=JobLifecycleStatus.succeeded,
            current_operation="Paper candidates selected for processing.",
            decisions=[
                SourceDecision(
                    claim_uuid=claim_uuid,
                    status=CandidateStatus.selected_ground_truth,
                    reason="paper_or_preprint_selected",
                )
            ],
        )


class FailingPipeline:
    def run_from_ingestion_payload(self, ingestion_payload, repository, qdrant_repository, vault_root):
        raise RuntimeError("metadata store unavailable")


def _override_dependencies(tmp_path):
    app.dependency_overrides[get_pipeline] = lambda: FakePipeline()
    app.dependency_overrides[get_repository] = lambda: object()
    app.dependency_overrides[get_qdrant_repository] = lambda: object()
    app.dependency_overrides[get_vault_root] = lambda: tmp_path / "vault"


def test_start_ground_truth_job_from_ingestion_fixture(monkeypatch, tmp_path):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    _override_dependencies(tmp_path)

    ingestion_response = client.post(
        "/ingestion/fixtures/transcript",
        json={
            "source_url": "https://www.tiktok.com/@fixture/video/1234567890",
            "transcript": "A paper says transformers scale well. The source is arXiv:1706.03762.",
        },
    )
    ingestion_payload = ingestion_response.json()

    response = client.post(f"/ground-truth/jobs/from-ingestion/{ingestion_payload['job_uuid']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ingestion_job_uuid"] == ingestion_payload["job_uuid"]
    assert payload["current_operation"] == "Paper candidates selected for processing."
    assert payload["decisions"][0]["status"] == "selected_ground_truth"

    fetched_ingestion = client.get(f"/ingestion/jobs/{ingestion_payload['job_uuid']}")
    assert fetched_ingestion.json()["claims"][0]["evidence_status"] == "pending"


def test_missing_ingestion_job_returns_404(tmp_path):
    _override_dependencies(tmp_path)

    response = client.post(f"/ground-truth/jobs/from-ingestion/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "ingestion_job_not_found"


def test_pipeline_failure_returns_failed_ground_truth_job(monkeypatch, tmp_path):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    _override_dependencies(tmp_path)
    app.dependency_overrides[get_pipeline] = lambda: FailingPipeline()

    ingestion_response = client.post(
        "/ingestion/fixtures/transcript",
        json={
            "source_url": "https://www.tiktok.com/@fixture/video/1234567890",
            "transcript": "The source is arXiv:1706.03762.",
        },
    )
    ingestion_payload = ingestion_response.json()

    response = client.post(f"/ground-truth/jobs/from-ingestion/{ingestion_payload['job_uuid']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["current_operation"] == "Ground-truth discovery failed."
    assert "RuntimeError: metadata store unavailable" in payload["error_message"]


def test_missing_ground_truth_job_returns_404():
    response = client.get(f"/ground-truth/jobs/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "ground_truth_job_not_found"
