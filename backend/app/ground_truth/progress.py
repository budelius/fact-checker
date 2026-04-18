from datetime import timezone
from uuid import UUID

from app.contracts.logging import build_pipeline_log_event
from app.schemas.ingestion import utc_now


def build_ground_truth_event(
    job_uuid: UUID,
    stage: str,
    status: str,
    message: str,
    entity_uuid: UUID | None = None,
) -> dict[str, str | None]:
    return build_pipeline_log_event(
        event_type="source_discovery",
        job_uuid=str(job_uuid),
        stage=stage,
        status=status,
        message=message,
        created_at=utc_now().astimezone(timezone.utc).isoformat(),
        entity_uuid=str(entity_uuid) if entity_uuid else None,
    )
