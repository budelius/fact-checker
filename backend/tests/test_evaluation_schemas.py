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


def test_extracted_claim_default_evidence_status_stays_pending():
    claim = ExtractedClaim(
        source_video_uuid=uuid4(),
        source_transcript_uuid=uuid4(),
        transcript_excerpt="The paper says attention is all you need.",
        claim_text="Transformers use attention.",
    )

    assert claim.evidence_status == EvidenceStatus.pending
    assert claim.model_dump(mode="json")["evidence_status"] == "pending"
