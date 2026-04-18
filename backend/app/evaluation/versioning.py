from dataclasses import dataclass
from uuid import UUID, NAMESPACE_URL, uuid5

from app.contracts.vault import expected_wiki_path
from app.ingestion.persistence import slugify
from app.schemas.evaluation import ReportVersion


@dataclass(frozen=True)
class ReportVersionIdentity:
    report_group_uuid: UUID
    report_uuid: UUID
    version: int
    slug: str
    markdown_path: str


def report_group_uuid(
    ingestion_job_uuid: UUID,
    ground_truth_job_uuid: UUID,
    source_video_uuid: UUID | None = None,
) -> UUID:
    source = source_video_uuid or ingestion_job_uuid
    return uuid5(NAMESPACE_URL, f"report-group:{source}:{ingestion_job_uuid}:{ground_truth_job_uuid}")


def next_version(previous_versions: list[ReportVersion] | None = None) -> int:
    if not previous_versions:
        return 1
    return max(version.version for version in previous_versions) + 1


def build_report_version_identity(
    *,
    ingestion_job_uuid: UUID,
    ground_truth_job_uuid: UUID,
    source_video_uuid: UUID | None = None,
    previous_versions: list[ReportVersion] | None = None,
    title: str = "fact-check-report",
) -> ReportVersionIdentity:
    group_uuid = report_group_uuid(ingestion_job_uuid, ground_truth_job_uuid, source_video_uuid)
    version = next_version(previous_versions)
    report_uuid = uuid5(group_uuid, f"version:{version}")
    slug = slugify(f"{title}-{str(group_uuid)[:8]}-v{version}")
    return ReportVersionIdentity(
        report_group_uuid=group_uuid,
        report_uuid=report_uuid,
        version=version,
        slug=slug,
        markdown_path=expected_wiki_path("reports", slug),
    )


def rerun_available(report: ReportVersion, latest_evidence_uuids: set[UUID] | list[UUID]) -> bool:
    previous = set(report.candidate_evidence_uuids) | set(report.cited_evidence_uuids)
    return bool(set(latest_evidence_uuids) - previous)
