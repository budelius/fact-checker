from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.ground_truth import (
    get_ground_truth_job,
    get_qdrant_repository,
    get_repository,
    get_vault_root,
)
from app.evaluation.evaluator import DeterministicEvaluator, OpenAIClaimEvaluator
from app.evaluation.pipeline import EvaluationPipeline
from app.evaluation.progress import initial_evaluation_stages
from app.ingestion.jobs import get_job
from app.schemas.evaluation import EvaluationJob, ReportVersion
from app.schemas.ground_truth import GroundTruthJob
from app.schemas.ingestion import JobLifecycleStatus, utc_now
from app.settings import Settings, get_settings

router = APIRouter(prefix="/reports", tags=["reports"])

_REPORT_JOB_STORE: dict[str, dict] = {}
_REPORT_STORE: dict[str, dict] = {}
_REPORT_VERSIONS_BY_GROUND_TRUTH: dict[str, list[dict]] = {}


def clear_report_jobs_for_tests() -> None:
    _REPORT_JOB_STORE.clear()
    _REPORT_STORE.clear()
    _REPORT_VERSIONS_BY_GROUND_TRUTH.clear()


def serialize_evaluation_job(job: EvaluationJob) -> dict:
    payload = jsonable_encoder(job)
    _REPORT_JOB_STORE[str(job.job_uuid)] = payload
    if job.report is not None:
        report_payload = jsonable_encoder(job.report)
        _REPORT_STORE[str(job.report.report_uuid)] = report_payload
        _REPORT_VERSIONS_BY_GROUND_TRUTH.setdefault(str(job.ground_truth_job_uuid), []).append(
            report_payload
        )
    return payload


def get_report_job(job_uuid: UUID) -> dict | None:
    return _REPORT_JOB_STORE.get(str(job_uuid))


def get_report(report_uuid: UUID) -> dict | None:
    return _REPORT_STORE.get(str(report_uuid))


def get_evaluation_pipeline(settings: Settings = Depends(get_settings)) -> EvaluationPipeline:
    evaluator = (
        OpenAIClaimEvaluator(settings)
        if settings.openai_api_key
        else DeterministicEvaluator()
    )
    return EvaluationPipeline(settings=settings, evaluator=evaluator)


def _previous_versions(ground_truth_job_uuid: UUID) -> list[ReportVersion]:
    return [
        ReportVersion.model_validate(payload)
        for payload in _REPORT_VERSIONS_BY_GROUND_TRUTH.get(str(ground_truth_job_uuid), [])
    ]


def _safe_pipeline_error(exc: Exception) -> str:
    message = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
    return f"{exc.__class__.__name__}: {message[:300]}"


def _failed_evaluation_job(
    ingestion_job_uuid: UUID,
    ground_truth_job_uuid: UUID,
    exc: Exception,
) -> EvaluationJob:
    message = _safe_pipeline_error(exc)
    now = utc_now()
    return EvaluationJob(
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        status=JobLifecycleStatus.failed,
        current_operation="Fact-check report generation failed.",
        stages=initial_evaluation_stages(),
        error_message=message,
        updated_at=now,
    )


def _run_report_job(
    ground_truth_job_uuid: UUID,
    pipeline: EvaluationPipeline,
    repository,
    qdrant_repository,
    vault_root: Path,
) -> dict:
    ground_truth_payload = get_ground_truth_job(ground_truth_job_uuid)
    if ground_truth_payload is None:
        raise HTTPException(status_code=404, detail="ground_truth_job_not_found")

    ground_truth = GroundTruthJob.model_validate(ground_truth_payload)
    ingestion_payload = get_job(ground_truth.ingestion_job_uuid)
    if ingestion_payload is None:
        raise HTTPException(status_code=404, detail="ingestion_job_not_found")
    if not ingestion_payload.get("claims"):
        raise HTTPException(status_code=400, detail="ground_truth_job_has_no_claims")

    try:
        job = pipeline.run_from_ground_truth(
            ground_truth,
            ingestion_payload,
            repository=repository,
            qdrant_repository=qdrant_repository,
            vault_root=vault_root,
            previous_versions=_previous_versions(ground_truth.job_uuid),
        )
    except Exception as exc:
        job = _failed_evaluation_job(
            ground_truth.ingestion_job_uuid,
            ground_truth.job_uuid,
            exc,
        )
    return serialize_evaluation_job(job)


@router.post("/jobs/from-ground-truth/{ground_truth_job_uuid}/rerun")
def rerun_report_job_from_ground_truth(
    ground_truth_job_uuid: UUID,
    pipeline: EvaluationPipeline = Depends(get_evaluation_pipeline),
    repository=Depends(get_repository),
    qdrant_repository=Depends(get_qdrant_repository),
    vault_root: Path = Depends(get_vault_root),
) -> dict:
    return _run_report_job(
        ground_truth_job_uuid,
        pipeline,
        repository,
        qdrant_repository,
        vault_root,
    )


@router.post("/jobs/from-ground-truth/{ground_truth_job_uuid}")
def start_report_job_from_ground_truth(
    ground_truth_job_uuid: UUID,
    pipeline: EvaluationPipeline = Depends(get_evaluation_pipeline),
    repository=Depends(get_repository),
    qdrant_repository=Depends(get_qdrant_repository),
    vault_root: Path = Depends(get_vault_root),
) -> dict:
    return _run_report_job(
        ground_truth_job_uuid,
        pipeline,
        repository,
        qdrant_repository,
        vault_root,
    )


@router.get("/jobs/{job_uuid}")
def fetch_report_job(job_uuid: UUID) -> dict:
    job = get_report_job(job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="report_job_not_found")
    return job


@router.get("/{report_uuid}")
def fetch_report(report_uuid: UUID) -> dict:
    report = get_report(report_uuid)
    if report is None:
        raise HTTPException(status_code=404, detail="report_not_found")
    return report
