from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.claims import EvidenceStatus, ExtractedClaim
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationJob,
    EvaluationLabel,
    EvaluationStage,
    EvaluationStageName,
    EvidenceCandidate,
    EvidenceCitation,
    EvidenceSourceKind,
    ReportVersion,
)
from app.evaluation.progress import (
    STAGE_ORDER,
    build_evaluation_event,
    fail_validation_stage,
    initial_evaluation_stages,
    update_evaluation_stage,
)
from app.schemas.ingestion import StageStatus


def test_evaluation_label_allows_expected_values():
    assert EvaluationLabel.supported == "supported"
    assert EvaluationLabel.contradicted == "contradicted"
    assert EvaluationLabel.mixed == "mixed"
    assert EvaluationLabel.insufficient == "insufficient"


def test_claim_evaluation_rejects_invalid_label():
    with pytest.raises(ValidationError):
        ClaimEvaluation(
            claim_uuid=uuid4(),
            claim_text="A model can reason perfectly.",
            label="true",
            rationale="Invalid legacy label.",
        )


def test_report_version_represents_citations_candidates_and_counts():
    claim_uuid = uuid4()
    evidence_uuid = uuid4()
    candidate = EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=evidence_uuid,
        title="Attention Is All You Need",
        raw_text="The Transformer allows significantly more parallelization.",
        source_url="https://arxiv.org/abs/1706.03762",
        chunk_id="chunk-1",
        publication_status="preprint",
        is_preprint=True,
    )
    citation = EvidenceCitation(
        claim_uuid=claim_uuid,
        evidence_uuid=evidence_uuid,
        title="Attention Is All You Need",
        source_url="https://arxiv.org/abs/1706.03762",
        chunk_id="chunk-1",
        excerpt="The Transformer allows significantly more parallelization.",
        publication_status="preprint",
        is_preprint=True,
    )
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="Transformers parallelize sequence modeling.",
        label=EvaluationLabel.supported,
        rationale="The cited chunk directly supports the parallelization claim.",
        citations=[citation],
        candidate_evidence=[candidate],
        preprint_notes=["The source is a preprint."],
    )

    report = ReportVersion(
        markdown_path="vault/wiki/reports/report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        claim_uuids=[claim_uuid],
        cited_evidence_uuids=[evidence_uuid],
        candidate_evidence_uuids=[candidate.uuid],
        label_counts={EvaluationLabel.supported: 1},
        narrative_markdown="The claim is supported by the cited paper chunk.",
        evaluations=[evaluation],
        cited_evidence=[citation],
        unused_candidate_evidence=[candidate],
    )

    payload = report.model_dump(mode="json")

    assert payload["label_counts"]["supported"] == 1
    assert payload["cited_evidence_uuids"] == [str(evidence_uuid)]
    assert payload["unused_candidate_evidence"][0]["source_kind"] == EvidenceSourceKind.paper_chunk


def test_evaluation_job_contains_progress_stage_and_report():
    report = ReportVersion(
        markdown_path="vault/wiki/reports/report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        narrative_markdown="No direct scientific evidence was available for now.",
    )

    job = EvaluationJob(
        ingestion_job_uuid=report.ingestion_job_uuid,
        ground_truth_job_uuid=report.ground_truth_job_uuid,
        stages=[EvaluationStage(name=EvaluationStageName.load_claims)],
        report=report,
        report_versions=[report],
    )

    assert job.current_operation == "Waiting to start evidence evaluation."
    assert job.stages[0].name == EvaluationStageName.load_claims
    assert job.report.markdown_path.endswith("report-v1.md")


def test_progress_helpers_expose_all_report_generation_steps():
    stages = initial_evaluation_stages()

    assert [stage.name for stage in stages] == STAGE_ORDER
    assert [stage.name.value for stage in stages] == [
        "load_claims",
        "load_evidence",
        "select_citations",
        "evaluate_claims",
        "validate_citations",
        "write_report",
        "index_and_link",
    ]


def test_progress_helpers_can_mark_failed_validation_stage():
    job = EvaluationJob(ingestion_job_uuid=uuid4(), ground_truth_job_uuid=uuid4())
    job.stages = initial_evaluation_stages()

    fail_validation_stage(job, "Uncited non-insufficient label rejected.")

    validation_stage = next(stage for stage in job.stages if stage.name == EvaluationStageName.validate_citations)
    assert validation_stage.status == StageStatus.failed
    assert job.current_operation == "Uncited non-insufficient label rejected."


def test_build_evaluation_event_uses_evaluation_event_type():
    job_uuid = uuid4()
    event = build_evaluation_event(
        job_uuid,
        EvaluationStageName.evaluate_claims,
        StageStatus.running,
        "Evaluating claims.",
    )

    assert event["event_type"] == "evaluation"
    assert event["job_uuid"] == str(job_uuid)
    assert event["stage"] == "evaluate_claims"
    assert event["status"] == "running"


def test_update_evaluation_stage_sets_current_operation():
    job = EvaluationJob(ingestion_job_uuid=uuid4(), ground_truth_job_uuid=uuid4())

    update_evaluation_stage(
        job,
        EvaluationStageName.load_claims,
        StageStatus.succeeded,
        "Loaded claims.",
    )

    assert job.stages[0].status == StageStatus.succeeded
    assert job.stages[0].completed_at is not None
    assert job.current_operation == "Loaded claims."


def test_extracted_claim_default_evidence_status_stays_pending():
    claim = ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt="The paper says attention is all you need.",
        claim_text="Transformers use attention.",
    )

    assert claim.evidence_status == EvidenceStatus.pending
    assert claim.model_dump(mode="json")["evidence_status"] == "pending"
