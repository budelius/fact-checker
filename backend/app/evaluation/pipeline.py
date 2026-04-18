from collections import Counter
from pathlib import Path
from uuid import UUID

from app.evaluation.evaluator import ClaimEvaluator, DeterministicEvaluator
from app.evaluation.evidence import select_claim_evidence
from app.evaluation.indexing import index_report_version
from app.evaluation.persistence import persist_report_knowledge
from app.evaluation.progress import (
    fail_validation_stage,
    initial_evaluation_stages,
    update_evaluation_stage,
)
from app.evaluation.validation import validate_claim_evaluations
from app.evaluation.versioning import build_report_version_identity
from app.schemas.claims import ExtractedClaim
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationJob,
    EvaluationLabel,
    EvaluationStageName,
    EvidenceCandidate,
    EvidenceCitation,
    ReportVersion,
)
from app.schemas.ground_truth import GroundTruthJob
from app.schemas.ingestion import JobLifecycleStatus, StageStatus, utc_now
from app.settings import Settings


def _claims_from_payload(ingestion_payload: dict) -> list[ExtractedClaim]:
    return [ExtractedClaim.model_validate(claim) for claim in ingestion_payload.get("claims", [])]


def _label_counts(evaluations: list[ClaimEvaluation]) -> dict[EvaluationLabel, int]:
    counts = Counter(evaluation.label for evaluation in evaluations)
    return {label: counts.get(label, 0) for label in EvaluationLabel}


def _all_citations(evaluations: list[ClaimEvaluation]) -> list[EvidenceCitation]:
    citations: list[EvidenceCitation] = []
    for evaluation in evaluations:
        citations.extend(evaluation.citations)
    return citations


def _all_unused_candidates(evaluations: list[ClaimEvaluation]) -> list[EvidenceCandidate]:
    candidates: list[EvidenceCandidate] = []
    for evaluation in evaluations:
        candidates.extend(evaluation.unused_candidate_evidence)
    return candidates


def _all_candidate_evidence_uuids(evaluations: list[ClaimEvaluation]) -> list[UUID]:
    seen: set[UUID] = set()
    ordered: list[UUID] = []
    for evaluation in evaluations:
        for candidate in [*evaluation.candidate_evidence, *evaluation.unused_candidate_evidence]:
            if candidate.evidence_uuid not in seen:
                seen.add(candidate.evidence_uuid)
                ordered.append(candidate.evidence_uuid)
    return ordered


def _build_narrative(evaluations: list[ClaimEvaluation]) -> str:
    counts = _label_counts(evaluations)
    total = len(evaluations)
    if total and counts[EvaluationLabel.insufficient] == total:
        return (
            "No direct scientific evidence was available for the checked claims for now. "
            "The report records the missing-evidence state instead of assigning unsupported truth."
        )
    parts = [f"Evaluated {total} claim{'s' if total != 1 else ''} against selected evidence."]
    parts.extend(
        f"{label.value}: {counts[label]}"
        for label in [
            EvaluationLabel.supported,
            EvaluationLabel.contradicted,
            EvaluationLabel.mixed,
            EvaluationLabel.insufficient,
        ]
    )
    return " ".join(parts)


class EvaluationPipeline:
    def __init__(
        self,
        settings: Settings | None = None,
        evaluator: ClaimEvaluator | None = None,
    ) -> None:
        self.settings = settings
        self.evaluator = evaluator or DeterministicEvaluator()

    def run_from_ground_truth(
        self,
        ground_truth_job: GroundTruthJob | dict,
        ingestion_payload: dict,
        repository,
        qdrant_repository,
        vault_root: Path,
        previous_versions: list[ReportVersion] | None = None,
    ) -> EvaluationJob:
        ground_truth = (
            ground_truth_job
            if isinstance(ground_truth_job, GroundTruthJob)
            else GroundTruthJob.model_validate(ground_truth_job)
        )
        claims = _claims_from_payload(ingestion_payload)
        job = EvaluationJob(
            ingestion_job_uuid=ground_truth.ingestion_job_uuid,
            ground_truth_job_uuid=ground_truth.job_uuid,
            status=JobLifecycleStatus.running,
            current_operation="Starting evidence evaluation.",
            stages=initial_evaluation_stages(),
        )

        update_evaluation_stage(
            job,
            EvaluationStageName.load_claims,
            StageStatus.succeeded,
            f"Loaded {len(claims)} extracted claims.",
        )
        evidence_sets = select_claim_evidence(
            claims,
            ground_truth,
            max_chunks_per_claim=(
                self.settings.evaluation_max_chunks_per_claim if self.settings else 8
            ),
            excerpt_max_chars=self.settings.evaluation_excerpt_max_chars if self.settings else 1200,
        )
        update_evaluation_stage(
            job,
            EvaluationStageName.load_evidence,
            StageStatus.succeeded,
            "Loaded selected source evidence.",
        )
        update_evaluation_stage(
            job,
            EvaluationStageName.select_citations,
            StageStatus.succeeded,
            "Prepared citation candidates.",
        )

        evaluator = (
            DeterministicEvaluator()
            if not any(evidence_set.candidates for evidence_set in evidence_sets.values())
            else self.evaluator
        )
        evaluations = evaluator.evaluate(claims, evidence_sets)
        update_evaluation_stage(
            job,
            EvaluationStageName.evaluate_claims,
            StageStatus.succeeded,
            f"Evaluated {len(evaluations)} claims.",
        )

        validation_errors = validate_claim_evaluations(
            [claim.uuid for claim in claims],
            evidence_sets,
            evaluations,
        )
        if validation_errors:
            job.status = JobLifecycleStatus.failed
            job.error_message = "evaluation_validation_failed"
            job.validation_errors = validation_errors
            fail_validation_stage(job, "Evaluation validation failed.")
            return job
        update_evaluation_stage(
            job,
            EvaluationStageName.validate_citations,
            StageStatus.succeeded,
            "Validated claim labels and citations.",
        )

        for evaluation in evaluations:
            evidence_set = evidence_sets.get(evaluation.claim_uuid)
            if evidence_set:
                evaluation.candidate_evidence = evidence_set.candidates
                evaluation.unused_candidate_evidence = evidence_set.unused_candidates
            if evaluation.transcript_excerpt is None:
                matching_claim = next(claim for claim in claims if claim.uuid == evaluation.claim_uuid)
                evaluation.transcript_excerpt = matching_claim.transcript_excerpt
                evaluation.screenshot_uuids = matching_claim.screenshot_uuids

        source_video_uuid = claims[0].source_video_uuid if claims else None
        identity = build_report_version_identity(
            ingestion_job_uuid=ground_truth.ingestion_job_uuid,
            ground_truth_job_uuid=ground_truth.job_uuid,
            source_video_uuid=source_video_uuid,
            previous_versions=previous_versions,
        )
        citations = _all_citations(evaluations)
        report = ReportVersion(
            report_uuid=identity.report_uuid,
            report_group_uuid=identity.report_group_uuid,
            version=identity.version,
            markdown_path=identity.markdown_path,
            ingestion_job_uuid=ground_truth.ingestion_job_uuid,
            ground_truth_job_uuid=ground_truth.job_uuid,
            source_video_uuid=source_video_uuid,
            claim_uuids=[claim.uuid for claim in claims],
            cited_evidence_uuids=[citation.evidence_uuid for citation in citations],
            candidate_evidence_uuids=_all_candidate_evidence_uuids(evaluations),
            label_counts=_label_counts(evaluations),
            narrative_markdown=_build_narrative(evaluations),
            source_policy_notes=[
                "Paper summaries are navigation only and were not used as verdict evidence."
            ],
            evaluations=evaluations,
            cited_evidence=citations,
            unused_candidate_evidence=_all_unused_candidates(evaluations),
        )
        persist_report_knowledge(repository, vault_root, report)
        update_evaluation_stage(
            job,
            EvaluationStageName.write_report,
            StageStatus.succeeded,
            "Wrote Markdown report and graph relationships.",
        )
        indexed_count = index_report_version(qdrant_repository, report)
        update_evaluation_stage(
            job,
            EvaluationStageName.index_and_link,
            StageStatus.succeeded if indexed_count else StageStatus.skipped,
            "Report indexing skipped; paper chunks remain indexed."
            if not indexed_count
            else f"Indexed {indexed_count} report chunks.",
        )
        job.report = report
        job.report_versions = [*(previous_versions or []), report]
        job.status = JobLifecycleStatus.succeeded
        job.current_operation = "Fact-check report generated."
        job.updated_at = utc_now()
        return job
