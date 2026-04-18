from datetime import timezone
from uuid import UUID

from app.contracts.logging import build_pipeline_log_event
from app.schemas.evaluation import EvaluationJob, EvaluationStage, EvaluationStageName
from app.schemas.ingestion import StageStatus, utc_now


STAGE_ORDER = [
    EvaluationStageName.load_claims,
    EvaluationStageName.load_evidence,
    EvaluationStageName.select_citations,
    EvaluationStageName.evaluate_claims,
    EvaluationStageName.validate_citations,
    EvaluationStageName.write_report,
    EvaluationStageName.index_and_link,
]


def initial_evaluation_stages() -> list[EvaluationStage]:
    return [EvaluationStage(name=stage) for stage in STAGE_ORDER]


def update_evaluation_stage(
    job: EvaluationJob,
    stage: EvaluationStageName,
    status: StageStatus,
    message: str,
    event_uuid: UUID | None = None,
) -> EvaluationJob:
    now = utc_now()
    target = next((existing for existing in job.stages if existing.name is stage), None)
    if target is None:
        target = EvaluationStage(name=stage)
        job.stages.append(target)

    target.status = status
    target.message = message
    target.event_uuid = event_uuid
    target.started_at = target.started_at or now
    target.completed_at = (
        now if status in {StageStatus.succeeded, StageStatus.failed, StageStatus.skipped} else None
    )
    job.current_operation = message
    job.updated_at = now
    return job


def fail_validation_stage(job: EvaluationJob, message: str) -> EvaluationJob:
    return update_evaluation_stage(
        job,
        EvaluationStageName.validate_citations,
        StageStatus.failed,
        message,
    )


def build_evaluation_event(
    job_uuid: UUID,
    stage: EvaluationStageName,
    status: StageStatus,
    message: str,
    entity_uuid: UUID | None = None,
) -> dict[str, str | None]:
    return build_pipeline_log_event(
        event_type="evaluation",
        job_uuid=str(job_uuid),
        stage=stage.value,
        status=status.value,
        message=message,
        created_at=utc_now().astimezone(timezone.utc).isoformat(),
        entity_uuid=str(entity_uuid) if entity_uuid else None,
    )
