from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder

from app.ingestion.progress import initial_stages
from app.schemas.ingestion import IngestionJob, JobLifecycleStatus, SourceKind, utc_now

_JOB_STORE: dict[str, dict] = {}


def create_ingestion_job(
    source_url: str,
    source_kind: SourceKind = SourceKind.tiktok_url,
) -> IngestionJob:
    return IngestionJob(
        source_kind=source_kind,
        source_url=source_url,
        status=JobLifecycleStatus.pending,
        current_operation="Ingestion job created.",
        stages=initial_stages(),
        video_uuid=uuid4(),
    )


def mark_job_failed(job: IngestionJob, message: str) -> IngestionJob:
    job.status = JobLifecycleStatus.failed
    job.current_operation = message
    job.error_message = message
    job.updated_at = utc_now()
    return job


def mark_job_succeeded(
    job: IngestionJob,
    message: str = "Claims extracted and ready for paper discovery.",
) -> IngestionJob:
    job.status = JobLifecycleStatus.succeeded
    job.current_operation = message
    job.updated_at = utc_now()
    return job


def serialize_job(job: IngestionJob, **extra: object) -> dict:
    payload = jsonable_encoder(job)
    payload.update(jsonable_encoder(extra))
    return payload


def save_job(payload: dict) -> dict:
    _JOB_STORE[str(payload["job_uuid"])] = payload
    return payload


def get_job(job_uuid: UUID) -> dict | None:
    return _JOB_STORE.get(str(job_uuid))


def clear_jobs_for_tests() -> None:
    _JOB_STORE.clear()
