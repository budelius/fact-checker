from app.schemas.evaluation import ReportVersion


def index_report_version(qdrant_repository, report: ReportVersion) -> int:
    if qdrant_repository is None:
        return 0
    if not hasattr(qdrant_repository, "upsert_payload"):
        return 0
    # Report text indexing is optional in Phase 4. Paper chunks remain the verdict evidence index.
    return 0
