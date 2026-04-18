from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.ground_truth import clear_ground_truth_jobs_for_tests, serialize_ground_truth_job
from app.api.reports import (
    clear_report_jobs_for_tests,
    get_evaluation_pipeline,
    get_qdrant_repository,
    get_repository,
    get_vault_root,
)
from app.ingestion.jobs import clear_jobs_for_tests, save_job
from app.main import app
from app.schemas.evaluation import EvaluationJob, ReportVersion
from app.schemas.ground_truth import GroundTruthJob
from app.schemas.ingestion import JobLifecycleStatus
from app.settings import get_settings

client = TestClient(app)


def setup_function(_function):
    clear_jobs_for_tests()
    clear_ground_truth_jobs_for_tests()
    clear_report_jobs_for_tests()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


class FakePipeline:
    def run_from_ground_truth(
        self,
        ground_truth_job,
        ingestion_payload,
        repository,
        qdrant_repository,
        vault_root,
        previous_versions=None,
    ):
        version = len(previous_versions or []) + 1
        report = ReportVersion(
            version=version,
            markdown_path=f"vault/wiki/reports/report-v{version}.md",
            ingestion_job_uuid=ground_truth_job.ingestion_job_uuid,
            ground_truth_job_uuid=ground_truth_job.job_uuid,
            claim_uuids=[ingestion_payload["claims"][0]["uuid"]],
            label_counts={"insufficient": 1},
            narrative_markdown="No direct scientific evidence was available for now.",
        )
        return EvaluationJob(
            ingestion_job_uuid=ground_truth_job.ingestion_job_uuid,
            ground_truth_job_uuid=ground_truth_job.job_uuid,
            status=JobLifecycleStatus.succeeded,
            current_operation="Fact-check report generated.",
            report=report,
            report_versions=[*(previous_versions or []), report],
        )


def _override_dependencies(tmp_path):
    app.dependency_overrides[get_evaluation_pipeline] = lambda: FakePipeline()
    app.dependency_overrides[get_repository] = lambda: object()
    app.dependency_overrides[get_qdrant_repository] = lambda: None
    app.dependency_overrides[get_vault_root] = lambda: tmp_path / "vault"


def _stored_ground_truth_with_ingestion() -> GroundTruthJob:
    ingestion_job_uuid = uuid4()
    save_job(
        {
            "job_uuid": str(ingestion_job_uuid),
            "claims": [
                {
                    "uuid": str(uuid4()),
                    "source_video_uuid": str(uuid4()),
                    "source_transcript_uuid": str(uuid4()),
                    "transcript_excerpt": "A claim.",
                    "claim_text": "A claim.",
                    "screenshot_uuids": [],
                    "evidence_status": "pending",
                    "source_candidate_count": 1,
                }
            ],
        }
    )
    ground_truth = GroundTruthJob(
        ingestion_job_uuid=ingestion_job_uuid,
        status=JobLifecycleStatus.succeeded,
    )
    serialize_ground_truth_job(ground_truth)
    return ground_truth


def test_start_report_job_from_ground_truth(tmp_path):
    _override_dependencies(tmp_path)
    ground_truth = _stored_ground_truth_with_ingestion()

    response = client.post(f"/reports/jobs/from-ground-truth/{ground_truth.job_uuid}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ground_truth_job_uuid"] == str(ground_truth.job_uuid)
    assert payload["status"] == "succeeded"
    assert payload["report"]["version"] == 1
    assert payload["report"]["markdown_path"] == "vault/wiki/reports/report-v1.md"


def test_fetch_report_job_and_report(tmp_path):
    _override_dependencies(tmp_path)
    ground_truth = _stored_ground_truth_with_ingestion()
    created = client.post(f"/reports/jobs/from-ground-truth/{ground_truth.job_uuid}").json()

    job_response = client.get(f"/reports/jobs/{created['job_uuid']}")
    report_response = client.get(f"/reports/{created['report']['report_uuid']}")

    assert job_response.status_code == 200
    assert report_response.status_code == 200
    assert report_response.json()["report_uuid"] == created["report"]["report_uuid"]


def test_missing_ground_truth_job_returns_404(tmp_path):
    _override_dependencies(tmp_path)

    response = client.post(f"/reports/jobs/from-ground-truth/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "ground_truth_job_not_found"


def test_rerun_creates_new_report_version(tmp_path):
    _override_dependencies(tmp_path)
    ground_truth = _stored_ground_truth_with_ingestion()

    first = client.post(f"/reports/jobs/from-ground-truth/{ground_truth.job_uuid}").json()
    second = client.post(f"/reports/jobs/from-ground-truth/{ground_truth.job_uuid}/rerun").json()

    assert first["report"]["version"] == 1
    assert second["report"]["version"] == 2
    assert first["report"]["report_uuid"] != second["report"]["report_uuid"]
