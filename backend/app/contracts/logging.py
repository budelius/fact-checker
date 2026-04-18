PIPELINE_EVENT_TYPES = (
    "ingestion",
    "search",
    "parsing",
    "evaluation",
    "indexing",
    "graph_write",
)

PIPELINE_EVENT_STATUSES = ("pending", "running", "succeeded", "failed", "skipped")

REQUIRED_PIPELINE_LOG_KEYS = (
    "event_type",
    "job_uuid",
    "stage",
    "status",
    "message",
    "created_at",
)


def build_pipeline_log_event(
    event_type: str,
    job_uuid: str,
    stage: str,
    status: str,
    message: str,
    created_at: str,
    entity_uuid: str | None = None,
) -> dict[str, str | None]:
    if event_type not in PIPELINE_EVENT_TYPES:
        raise ValueError(f"Unsupported pipeline event type: {event_type}")
    if status not in PIPELINE_EVENT_STATUSES:
        raise ValueError(f"Unsupported pipeline event status: {status}")

    return {
        "event_type": event_type,
        "job_uuid": job_uuid,
        "stage": stage,
        "status": status,
        "message": message,
        "created_at": created_at,
        "entity_uuid": entity_uuid,
    }
