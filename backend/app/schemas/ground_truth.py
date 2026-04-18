from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.schemas.ingestion import JobLifecycleStatus, StageStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GroundTruthStageName(str, Enum):
    load_claims = "load_claims"
    generate_queries = "generate_queries"
    search_openai_web = "search_openai_web"
    search_paper_indexes = "search_paper_indexes"
    merge_candidates = "merge_candidates"
    select_sources = "select_sources"
    acquire_papers = "acquire_papers"
    parse_papers = "parse_papers"
    summarize_papers = "summarize_papers"
    index_chunks = "index_chunks"
    write_owned_artifacts = "write_owned_artifacts"


class SourceProvider(str, Enum):
    phase2_hint = "phase2_hint"
    openai_web = "openai_web"
    arxiv = "arxiv"
    openalex = "openalex"
    semantic_scholar = "semantic_scholar"


class CandidateKind(str, Enum):
    paper = "paper"
    preprint = "preprint"
    non_paper = "non_paper"
    unknown = "unknown"


class CandidateStatus(str, Enum):
    selected_ground_truth = "selected_ground_truth"
    rejected = "rejected"
    supplemental = "supplemental"
    no_paper_found = "no_paper_found"
    needs_manual_review = "needs_manual_review"


class PaperProcessingStatus(str, Enum):
    metadata_only = "metadata_only"
    linked = "linked"
    downloaded = "downloaded"
    parsed = "parsed"
    chunked = "chunked"
    summarized = "summarized"
    indexed = "indexed"
    failed = "failed"


class ExternalPaperId(BaseModel):
    provider: str
    value: str


class DiscoveryPath(BaseModel):
    provider: SourceProvider
    query: str | None = None
    source_candidate_uuid: UUID | None = None
    result_rank: int | None = None
    url: str | None = None
    note: str | None = None


class GroundTruthStage(BaseModel):
    name: GroundTruthStageName
    status: StageStatus = StageStatus.pending
    message: str | None = None
    event_uuid: UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class GroundTruthArtifact(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    artifact_type: str
    vault_path: str | None = None
    source_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaperAuthor(BaseModel):
    name: str
    external_ids: list[ExternalPaperId] = Field(default_factory=list)


class PaperCandidate(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    kind: CandidateKind = CandidateKind.unknown
    status: CandidateStatus = CandidateStatus.needs_manual_review
    external_ids: list[ExternalPaperId] = Field(default_factory=list)
    authors: list[PaperAuthor] = Field(default_factory=list)
    abstract: str | None = None
    publication_date: date | None = None
    source_url: str | None = None
    pdf_url: str | None = None
    landing_page_url: str | None = None
    confidence: float | None = None
    discovery_paths: list[DiscoveryPath] = Field(default_factory=list)
    raw_provider_data: dict[str, Any] = Field(default_factory=dict)
    selected_reason: str | None = None
    rejected_reason: str | None = None


class SourceDecision(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    claim_uuid: UUID | None = None
    candidate_uuid: UUID | None = None
    status: CandidateStatus
    reason: str
    provenance: dict[str, Any] = Field(default_factory=dict)


class PaperMetadata(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    title: str
    authors: list[PaperAuthor] = Field(default_factory=list)
    external_ids: list[ExternalPaperId] = Field(default_factory=list)
    publication_status: str
    publication_date: date | None = None
    abstract: str | None = None
    source_links: list[str] = Field(default_factory=list)
    pdf_url: str | None = None
    vault_path: str | None = None
    processing_status: PaperProcessingStatus = PaperProcessingStatus.metadata_only


class PaperAcquisition(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    paper_uuid: UUID
    source_url: str | None = None
    pdf_url: str | None = None
    raw_pdf_path: str | None = None
    status: PaperProcessingStatus
    reason: str
    bytes_downloaded: int | None = None


class PaperChunk(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    paper_uuid: UUID
    source_uuid: UUID
    chunk_id: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    section: str | None = None
    vault_path: str
    source_url: str


class PaperSummary(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    paper_uuid: UUID
    summary_markdown: str
    methods: list[str] = Field(default_factory=list)
    key_claims: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class GroundTruthJob(BaseModel):
    job_uuid: UUID = Field(default_factory=uuid4)
    ingestion_job_uuid: UUID
    status: JobLifecycleStatus = JobLifecycleStatus.pending
    current_operation: str = "Waiting to start ground-truth discovery."
    stages: list[GroundTruthStage] = Field(default_factory=list)
    artifacts: list[GroundTruthArtifact] = Field(default_factory=list)
    candidates: list[PaperCandidate] = Field(default_factory=list)
    decisions: list[SourceDecision] = Field(default_factory=list)
    papers: list[PaperMetadata] = Field(default_factory=list)
    chunks: list[PaperChunk] = Field(default_factory=list)
    summaries: list[PaperSummary] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error_message: str | None = None
