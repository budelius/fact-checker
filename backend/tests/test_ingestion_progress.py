from uuid import uuid4

from app.ingestion.jobs import create_ingestion_job
from app.ingestion.progress import STAGE_ORDER, build_stage_log, initial_stages, update_stage
from app.schemas.ingestion import IngestionStageName, StageStatus


def test_initial_stages_match_ui_contract():
    assert [stage.value for stage in STAGE_ORDER] == [
        "validate_url",
        "read_public_metadata",
        "build_transcript",
        "capture_source_clues",
        "extract_claims",
        "triage_research_basis",
        "write_owned_artifacts",
    ]
    assert [stage.name for stage in initial_stages()] == STAGE_ORDER


def test_update_build_transcript_changes_current_operation():
    job = create_ingestion_job("https://www.tiktok.com/@fixture/video/1234567890")

    update_stage(
        job,
        IngestionStageName.build_transcript,
        StageStatus.running,
        "Building transcript",
    )

    assert job.current_operation == "Building transcript"
    assert job.stages[2].status is StageStatus.running


def test_build_stage_log_contains_required_keys():
    job = create_ingestion_job("https://www.tiktok.com/@fixture/video/1234567890")
    entity_uuid = uuid4()

    event = build_stage_log(
        job,
        IngestionStageName.build_transcript,
        StageStatus.succeeded,
        "Transcript ready",
        entity_uuid=entity_uuid,
    )

    assert event["event_type"] == "ingestion"
    assert event["job_uuid"] == str(job.job_uuid)
    assert event["stage"] == "build_transcript"
    assert event["status"] == "succeeded"
    assert event["entity_uuid"] == str(entity_uuid)
