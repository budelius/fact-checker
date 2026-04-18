from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.ingestion import JobLifecycleStatus, StageStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvaluationLabel(str, Enum):
    supported = "supported"
    contradicted = "contradicted"
    mixed = "mixed"
    insufficient = "insufficient"


class EvaluationStageName(str, Enum):
    load_claims = "load_claims"
    load_evidence = "load_evidence"
    select_citations = "select_citations"
    evaluate_claims = "evaluate_claims"
    validate_citations = "validate_citations"
    write_report = "write_report"
    index_and_link = "index_and_link"


class EvidenceSourceKind(str, Enum):
    paper_chunk = "paper_chunk"
    direct_source_text = "direct_source_text"
    news_article = "news_article"
    paper_summary = "paper_summary"


class EvaluationStage(BaseModel):
    name: EvaluationStageName
    status: StageStatus = StageStatus.pending
    message: str | None = None
    event_uuid: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class EvidenceCandidate(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    claim_uuid: UUID
    evidence_uuid: UUID
    source_kind: EvidenceSourceKind = EvidenceSourceKind.paper_chunk
    title: str
    raw_text: str
    excerpt: str | None = None
    source_url: str
    paper_uuid: UUID | None = None
    source_uuid: UUID | None = None
    candidate_uuid: UUID | None = None
    chunk_id: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    section: str | None = None
    publication_status: str | None = None
    is_preprint: bool = False
    source_policy_notes: list[str] = Field(default_factory=list)
    selection_status: str | None = None
    used_as_citation: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceCitation(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    claim_uuid: UUID
    evidence_uuid: UUID
    source_kind: EvidenceSourceKind = EvidenceSourceKind.paper_chunk
    title: str
    source_url: str
    paper_uuid: UUID | None = None
    source_uuid: UUID | None = None
    candidate_uuid: UUID | None = None
    chunk_id: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    section: str | None = None
    excerpt: str
    publication_status: str | None = None
    is_preprint: bool = False
    source_policy_notes: list[str] = Field(default_factory=list)


class SubclaimEvaluation(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    text: str
    label: EvaluationLabel
    rationale: str
    citation_uuids: list[UUID] = Field(default_factory=list)
    uncertainty_note: str | None = None
    overclaim_note: str | None = None


class ClaimEvaluation(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    claim_uuid: UUID
    claim_text: str
    label: EvaluationLabel
    rationale: str
    citations: list[EvidenceCitation] = Field(default_factory=list)
    candidate_evidence: list[EvidenceCandidate] = Field(default_factory=list)
    unused_candidate_evidence: list[EvidenceCandidate] = Field(default_factory=list)
    subclaims: list[SubclaimEvaluation] = Field(default_factory=list)
    uncertainty_note: str | None = None
    overclaim_note: str | None = None
    source_limit_notes: list[str] = Field(default_factory=list)
    preprint_notes: list[str] = Field(default_factory=list)
    news_exception: bool = False
    transcript_excerpt: str | None = None
    screenshot_uuids: list[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class EvaluationValidationError(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    claim_uuid: UUID | None = None
    evidence_uuid: UUID | None = None
    code: str
    message: str


class ReportVersion(BaseModel):
    report_uuid: UUID = Field(default_factory=uuid4)
    report_group_uuid: UUID = Field(default_factory=uuid4)
    version: int = 1
    markdown_path: str
    ingestion_job_uuid: UUID
    ground_truth_job_uuid: UUID
    source_video_uuid: UUID | None = None
    claim_uuids: list[UUID] = Field(default_factory=list)
    cited_evidence_uuids: list[UUID] = Field(default_factory=list)
    candidate_evidence_uuids: list[UUID] = Field(default_factory=list)
    label_counts: dict[EvaluationLabel, int] = Field(default_factory=dict)
    narrative_markdown: str
    source_policy_notes: list[str] = Field(default_factory=list)
    evaluations: list[ClaimEvaluation] = Field(default_factory=list)
    cited_evidence: list[EvidenceCitation] = Field(default_factory=list)
    unused_candidate_evidence: list[EvidenceCandidate] = Field(default_factory=list)
    validation_errors: list[EvaluationValidationError] = Field(default_factory=list)
    rerun_available: bool = False
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class EvaluationJob(BaseModel):
    job_uuid: UUID = Field(default_factory=uuid4)
    ingestion_job_uuid: UUID
    ground_truth_job_uuid: UUID
    status: JobLifecycleStatus = JobLifecycleStatus.pending
    current_operation: str = "Waiting to start evidence evaluation."
    stages: list[EvaluationStage] = Field(default_factory=list)
    report: ReportVersion | None = None
    report_versions: list[ReportVersion] = Field(default_factory=list)
    validation_errors: list[EvaluationValidationError] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error_message: str | None = None
