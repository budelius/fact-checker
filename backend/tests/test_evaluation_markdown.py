from uuid import uuid4

from app.evaluation.evaluator import citation_from_candidate
from app.evaluation.markdown import PAPER_SUMMARY_WARNING, build_report_markdown
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationLabel,
    EvidenceCandidate,
    ReportVersion,
)


def _candidate(claim_uuid):
    return EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=uuid4(),
        title="Attention Is All You Need",
        raw_text="The Transformer allows significantly more parallelization.",
        source_url="https://arxiv.org/abs/1706.03762",
        chunk_id="chunk-1",
        publication_status="preprint",
        is_preprint=True,
        selection_status="selected_ground_truth",
    )


def _report() -> ReportVersion:
    claim_uuid = uuid4()
    candidate = _candidate(claim_uuid)
    citation = citation_from_candidate(candidate)
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="Transformers parallelize sequence modeling.",
        label=EvaluationLabel.supported,
        rationale="The cited chunk supports the claim.",
        citations=[citation],
        candidate_evidence=[candidate],
        preprint_notes=["The cited source is a preprint."],
    )
    unused = EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=uuid4(),
        title="Attention blog",
        raw_text="Supplemental blog only.",
        source_url="https://example.com/blog",
        selection_status="supplemental",
    )
    return ReportVersion(
        markdown_path="vault/wiki/reports/attention-report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        claim_uuids=[claim_uuid],
        cited_evidence_uuids=[candidate.evidence_uuid],
        candidate_evidence_uuids=[candidate.uuid, unused.uuid],
        label_counts={EvaluationLabel.supported: 1},
        narrative_markdown="The video claim is supported by a selected paper chunk.",
        evaluations=[evaluation],
        cited_evidence=[citation],
        unused_candidate_evidence=[unused],
    )


def test_report_template_contains_phase_4_frontmatter_keys():
    template = open("../vault/templates/report.md", encoding="utf-8").read()

    assert "report_uuid" in template
    assert "cited_evidence_uuids" in template
    assert "candidate_evidence_uuids" in template


def test_build_report_markdown_contains_required_sections_and_warning():
    markdown = build_report_markdown(_report())

    assert "# Fact-check report" in markdown
    assert "## Narrative report" in markdown
    assert "## Claims checked" in markdown
    assert "## Evidence used" in markdown
    assert "## Candidate evidence reviewed" in markdown
    assert "## Provenance" in markdown
    assert PAPER_SUMMARY_WARNING in markdown


def test_build_report_markdown_includes_cited_and_unused_evidence_sections():
    markdown = build_report_markdown(_report())

    assert "Attention Is All You Need" in markdown
    assert "chunk `chunk-1`" in markdown
    assert "Attention blog" in markdown
    assert "supplemental" in markdown


def test_uncertainty_only_renders_for_mixed_or_insufficient():
    report = _report()
    report.evaluations[0].uncertainty_note = "Should not render for supported labels."

    markdown = build_report_markdown(report)

    assert "Should not render for supported labels" not in markdown
