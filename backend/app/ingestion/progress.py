from datetime import timezone
from uuid import UUID

from app.contracts.logging import build_pipeline_log_event
from app.schemas.ingestion import (
    IngestionJob,
    IngestionStage,
    IngestionStageName,
    StageStatus,
    utc_now,
)

STAGE_ORDER = [
    IngestionStageName.validate_url,
    IngestionStageName.read_public_metadata,
    IngestionStageName.build_transcript,
    IngestionStageName.capture_source_clues,
    IngestionStageName.extract_claims,
    IngestionStageName.triage_research_basis,
    IngestionStageName.write_owned_artifacts,
]


def initial_stages() -> list[IngestionStage]:
    return [IngestionStage(name=stage) for stage in STAGE_ORDER]


def update_stage(
    job: IngestionJob,
    stage: IngestionStageName,
    status: StageStatus,
    message: str,
    entity_uuid: UUID | None = None,
) -> IngestionJob:
    now = utc_now()
    target = next((existing for existing in job.stages if existing.name is stage), None)
    if target is None:
        target = IngestionStage(name=stage)
        job.stages.append(target)

    target.status = status
    target.message = message
    target.entity_uuid = entity_uuid
    target.started_at = target.started_at or now
    target.finished_at = (
        now if status in {StageStatus.succeeded, StageStatus.failed, StageStatus.skipped} else None
    )
    job.current_operation = message
    job.updated_at = now
    return job


def build_stage_log(
    job: IngestionJob,
    stage: IngestionStageName,
    status: StageStatus,
    message: str,
    entity_uuid: UUID | None = None,
) -> dict:
    return build_pipeline_log_event(
        event_type="ingestion",
        job_uuid=str(job.job_uuid),
        stage=stage.value,
        status=status.value,
        message=message,
        created_at=utc_now().astimezone(timezone.utc).isoformat(),
        entity_uuid=str(entity_uuid) if entity_uuid else None,
    )
