from uuid import uuid4

from app.evaluation.evaluator import FakeEvaluator
from app.evaluation.pipeline import EvaluationPipeline
from app.schemas.claims import ExtractedClaim
from app.schemas.evaluation import ClaimEvaluation, EvaluationLabel
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    GroundTruthJob,
    PaperCandidate,
    PaperChunk,
    PaperMetadata,
    PaperSummary,
    SourceDecision,
)
from app.schemas.ingestion import JobLifecycleStatus
from app.settings import Settings


class FakeRepository:
    def __init__(self) -> None:
        self.entities = []
        self.relationships = []

    def upsert_entity(self, entity) -> None:
        self.entities.append(entity)

    def upsert_relationship(self, relationship) -> None:
        self.relationships.append(relationship)


def _settings(monkeypatch, tmp_path) -> Settings:
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    return Settings()


def _claim(text: str) -> ExtractedClaim:
    return ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt=text,
        claim_text=text,
    )


def _ingestion_payload(claims: list[ExtractedClaim]) -> dict:
    return {
        "job_uuid": str(uuid4()),
        "claims": [claim.model_dump(mode="json") for claim in claims],
    }


def _ground_truth_job(claims: list[ExtractedClaim], include_chunks: bool = True) -> GroundTruthJob:
    paper_uuid = uuid4()
    supplemental_uuid = uuid4()
    chunks = [
        PaperChunk(
            paper_uuid=paper_uuid,
            source_uuid=paper_uuid,
            chunk_id="chunk-1",
            text="The Transformer allows significantly more parallelization.",
            vault_path="vault/wiki/papers/attention.md",
            source_url="https://arxiv.org/abs/1706.03762",
        )
    ] if include_chunks else []
    return GroundTruthJob(
        ingestion_job_uuid=uuid4(),
        status=JobLifecycleStatus.succeeded,
        candidates=[
            PaperCandidate(
                uuid=paper_uuid,
                title="Attention Is All You Need",
                kind=CandidateKind.preprint,
                status=CandidateStatus.selected_ground_truth,
                source_url="https://arxiv.org/abs/1706.03762",
            ),
            PaperCandidate(
                uuid=supplemental_uuid,
                title="Supplemental blog",
                kind=CandidateKind.non_paper,
                status=CandidateStatus.supplemental,
                source_url="https://example.com/blog",
            ),
        ],
        decisions=[
            *[
                SourceDecision(
                    claim_uuid=claim.uuid,
                    candidate_uuid=paper_uuid,
                    status=CandidateStatus.selected_ground_truth,
                    reason="selected paper",
                )
                for claim in claims
            ],
            SourceDecision(
                claim_uuid=claims[0].uuid,
                candidate_uuid=supplemental_uuid,
                status=CandidateStatus.supplemental,
                reason="unused supplemental source",
            ),
        ],
        papers=[
            PaperMetadata(
                uuid=paper_uuid,
                title="Attention Is All You Need",
                publication_status="preprint",
                source_links=["https://arxiv.org/abs/1706.03762"],
            )
        ],
        chunks=chunks,
        summaries=[
            PaperSummary(
                paper_uuid=paper_uuid,
                summary_markdown="Generated summary that must not be cited.",
            )
        ],
    )


def test_evaluation_pipeline_generates_cited_report(monkeypatch, tmp_path):
    settings = _settings(monkeypatch, tmp_path)
    claims = [_claim("Transformers parallelize sequence modeling.")]
    ground_truth = _ground_truth_job(claims)
    repository = FakeRepository()

    job = EvaluationPipeline(settings=settings).run_from_ground_truth(
        ground_truth,
        _ingestion_payload(claims),
        repository=repository,
        qdrant_repository=None,
        vault_root=tmp_path / "vault",
    )

    assert job.status == JobLifecycleStatus.succeeded
    assert job.report is not None
    assert len(job.report.evaluations) == 1
    assert job.report.evaluations[0].label == EvaluationLabel.supported
    assert job.report.evaluations[0].citations[0].source_url
    assert (tmp_path / "vault" / "wiki" / "reports").exists()
    assert repository.entities[0].entity_type.value == "report"


def test_evaluation_pipeline_handles_no_paper_chunks_as_insufficient(monkeypatch, tmp_path):
    settings = _settings(monkeypatch, tmp_path)
    claims = [_claim("A claim without direct paper evidence.")]
    repository = FakeRepository()

    job = EvaluationPipeline(settings=settings).run_from_ground_truth(
        _ground_truth_job(claims, include_chunks=False),
        _ingestion_payload(claims),
        repository=repository,
        qdrant_repository=None,
        vault_root=tmp_path / "vault",
    )

    assert job.status == JobLifecycleStatus.succeeded
    assert job.report is not None
    assert job.report.evaluations[0].label == EvaluationLabel.insufficient
    assert "No direct scientific evidence" in job.report.narrative_markdown


def test_evaluation_pipeline_validation_failure_prevents_persistence(monkeypatch, tmp_path):
    settings = _settings(monkeypatch, tmp_path)
    claims = [_claim("A claim with invalid uncited support.")]
    invalid = ClaimEvaluation(
        claim_uuid=claims[0].uuid,
        claim_text=claims[0].claim_text,
        label=EvaluationLabel.supported,
        rationale="Uncited support should fail validation.",
    )
    repository = FakeRepository()

    job = EvaluationPipeline(settings=settings, evaluator=FakeEvaluator([invalid])).run_from_ground_truth(
        _ground_truth_job(claims),
        _ingestion_payload(claims),
        repository=repository,
        qdrant_repository=None,
        vault_root=tmp_path / "vault",
    )

    assert job.status == JobLifecycleStatus.failed
    assert job.validation_errors[0].code == "uncited_non_insufficient_label"
    assert repository.entities == []
    assert not (tmp_path / "vault" / "wiki" / "reports").exists()


def test_evaluation_pipeline_accepts_fake_mixed_result_with_citation(monkeypatch, tmp_path):
    settings = _settings(monkeypatch, tmp_path)
    claims = [_claim("Transformers solve all sequence modeling problems.")]
    ground_truth = _ground_truth_job(claims)
    candidate_job = EvaluationPipeline(settings=settings).run_from_ground_truth(
        ground_truth,
        _ingestion_payload(claims),
        repository=FakeRepository(),
        qdrant_repository=None,
        vault_root=tmp_path / "first" / "vault",
    )
    citation = candidate_job.report.evaluations[0].citations[0]
    mixed = ClaimEvaluation(
        claim_uuid=claims[0].uuid,
        claim_text=claims[0].claim_text,
        label=EvaluationLabel.mixed,
        rationale="The evidence supports parallelization but not the sweeping claim.",
        citations=[citation],
        uncertainty_note="Scope mismatch.",
        overclaim_note="The creator overstates the paper.",
    )

    job = EvaluationPipeline(settings=settings, evaluator=FakeEvaluator([mixed])).run_from_ground_truth(
        ground_truth,
        _ingestion_payload(claims),
        repository=FakeRepository(),
        qdrant_repository=None,
        vault_root=tmp_path / "second" / "vault",
    )

    assert job.status == JobLifecycleStatus.succeeded
    assert job.report.evaluations[0].label == EvaluationLabel.mixed
