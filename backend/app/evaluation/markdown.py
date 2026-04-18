from datetime import UTC, datetime
from uuid import UUID

import yaml

from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationLabel,
    EvidenceCandidate,
    EvidenceCitation,
    ReportVersion,
)

PAPER_SUMMARY_WARNING = "Paper summaries are navigation only and were not used as verdict evidence."


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _uuid_list(values: list[UUID]) -> list[str]:
    return [str(value) for value in values]


def _label_counts(report: ReportVersion) -> dict[str, int]:
    if report.label_counts:
        return {
            (key.value if isinstance(key, EvaluationLabel) else str(key)): value
            for key, value in report.label_counts.items()
        }
    counts = {label.value: 0 for label in EvaluationLabel}
    for evaluation in report.evaluations:
        counts[evaluation.label.value] += 1
    return counts


def _frontmatter(report: ReportVersion) -> dict:
    now = _now_iso()
    return {
        "report_uuid": str(report.report_uuid),
        "report_group_uuid": str(report.report_group_uuid),
        "version": report.version,
        "entity_type": "report",
        "ingestion_job_uuid": str(report.ingestion_job_uuid),
        "ground_truth_job_uuid": str(report.ground_truth_job_uuid),
        "video_uuid": str(report.source_video_uuid) if report.source_video_uuid else None,
        "claim_uuids": _uuid_list(report.claim_uuids),
        "cited_evidence_uuids": _uuid_list(report.cited_evidence_uuids),
        "candidate_evidence_uuids": _uuid_list(report.candidate_evidence_uuids),
        "label_counts": _label_counts(report),
        "source_policy": report.source_policy_notes,
        "provenance_refs": [
            str(candidate.uuid) for candidate in report.unused_candidate_evidence
        ],
        "created_at": report.created_at.isoformat() if report.created_at else now,
        "updated_at": report.updated_at.isoformat() if report.updated_at else now,
    }


def _citation_lines(citations: list[EvidenceCitation]) -> str:
    if not citations:
        return "- No citations."
    lines = []
    for citation in citations:
        location = ", ".join(
            value
            for value in [
                f"chunk `{citation.chunk_id}`" if citation.chunk_id else "",
                f"section {citation.section}" if citation.section else "",
                f"pages {citation.page_start}-{citation.page_end}"
                if citation.page_start is not None and citation.page_end is not None
                else "",
            ]
            if value
        )
        preprint = " Preprint/source status: " + citation.publication_status if citation.publication_status else ""
        lines.append(
            f"- `{citation.evidence_uuid}` {citation.title}"
            + (f" ({location})" if location else "")
            + f" - {citation.source_url}.{preprint}\n"
            + f"  - Excerpt: {citation.excerpt}"
        )
    return "\n".join(lines)


def _candidate_lines(candidates: list[EvidenceCandidate]) -> str:
    if not candidates:
        return "- No unused candidate evidence recorded."
    return "\n".join(
        f"- `{candidate.evidence_uuid}` {candidate.title}"
        f" ({candidate.selection_status or candidate.source_kind.value}) - {candidate.source_url}"
        for candidate in candidates
    )


def _claim_line(evaluation: ClaimEvaluation) -> str:
    lines = [
        f"### {evaluation.label.value}: {evaluation.claim_text}",
        "",
        f"- Claim UUID: `{evaluation.claim_uuid}`",
        f"- Rationale: {evaluation.rationale}",
    ]
    if evaluation.overclaim_note:
        lines.append(f"- Overclaim note: {evaluation.overclaim_note}")
    if evaluation.label in {EvaluationLabel.mixed, EvaluationLabel.insufficient}:
        if evaluation.uncertainty_note:
            lines.append(f"- Uncertainty: {evaluation.uncertainty_note}")
    if evaluation.preprint_notes:
        lines.append("- Preprint/source status:")
        lines.extend(f"  - {note}" for note in evaluation.preprint_notes)
    if evaluation.source_limit_notes:
        lines.append("- Source limits:")
        lines.extend(f"  - {note}" for note in evaluation.source_limit_notes)
    if evaluation.news_exception:
        lines.append("- Non-scientific source exception")
    lines.extend(["", "Citations:", _citation_lines(evaluation.citations)])
    return "\n".join(lines)


def _all_citations(report: ReportVersion) -> list[EvidenceCitation]:
    if report.cited_evidence:
        return report.cited_evidence
    citations: list[EvidenceCitation] = []
    for evaluation in report.evaluations:
        citations.extend(evaluation.citations)
    return citations


def build_report_markdown(report: ReportVersion) -> str:
    frontmatter = yaml.safe_dump(
        _frontmatter(report),
        sort_keys=False,
        allow_unicode=False,
    ).strip()
    claim_sections = "\n\n".join(_claim_line(evaluation) for evaluation in report.evaluations)
    if not claim_sections:
        claim_sections = "No claim evaluations recorded."
    cited = _citation_lines(_all_citations(report))
    unused = _candidate_lines(report.unused_candidate_evidence)
    validation = (
        "- No validation errors."
        if not report.validation_errors
        else "\n".join(
            f"- `{error.code}`"
            + (f" claim `{error.claim_uuid}`" if error.claim_uuid else "")
            + f": {error.message}"
            for error in report.validation_errors
        )
    )

    return "\n".join(
        [
            "---",
            frontmatter,
            "---",
            "",
            "# Fact-check report",
            "",
            "## Narrative report",
            "",
            report.narrative_markdown,
            "",
            "## Claims checked",
            "",
            claim_sections,
            "",
            "## Evidence used",
            "",
            cited,
            "",
            "## Candidate evidence reviewed",
            "",
            unused,
            "",
            "## Provenance",
            "",
            f"- Report UUID: `{report.report_uuid}`",
            f"- Report group UUID: `{report.report_group_uuid}`",
            f"- Version: {report.version}",
            f"- Markdown path: `{report.markdown_path}`",
            f"- Rerun available: {str(report.rerun_available).lower()}",
            f"- {PAPER_SUMMARY_WARNING}",
            "",
            "### Validation",
            "",
            validation,
            "",
        ]
    )
