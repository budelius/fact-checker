from uuid import uuid4

from app.evaluation.versioning import build_report_version_identity, rerun_available
from app.schemas.evaluation import ReportVersion


def test_report_version_identity_creates_distinct_rerun_paths():
    ingestion_job_uuid = uuid4()
    ground_truth_job_uuid = uuid4()

    first_identity = build_report_version_identity(
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        title="attention report",
    )
    first_report = ReportVersion(
        report_uuid=first_identity.report_uuid,
        report_group_uuid=first_identity.report_group_uuid,
        version=first_identity.version,
        markdown_path=first_identity.markdown_path,
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        narrative_markdown="First version.",
    )
    second_identity = build_report_version_identity(
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        previous_versions=[first_report],
        title="attention report",
    )

    assert first_identity.version == 1
    assert second_identity.version == 2
    assert first_identity.report_group_uuid == second_identity.report_group_uuid
    assert first_identity.report_uuid != second_identity.report_uuid
    assert first_identity.markdown_path != second_identity.markdown_path
    assert first_report.markdown_path == first_identity.markdown_path


def test_rerun_available_when_new_evidence_chunk_appears():
    known_evidence_uuid = uuid4()
    new_evidence_uuid = uuid4()
    report = ReportVersion(
        markdown_path="vault/wiki/reports/report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        narrative_markdown="First version.",
        candidate_evidence_uuids=[known_evidence_uuid],
    )

    assert rerun_available(report, [known_evidence_uuid]) is False
    assert rerun_available(report, [known_evidence_uuid, new_evidence_uuid]) is True
