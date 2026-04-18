from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from uuid import UUID

from app.evaluation.evidence import ClaimEvidenceSet
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationLabel,
    EvaluationValidationError,
    EvidenceCandidate,
    EvidenceCitation,
    EvidenceSourceKind,
)


class EvaluationValidationFailure(ValueError):
    def __init__(self, errors: list[EvaluationValidationError]) -> None:
        self.errors = errors
        super().__init__("evaluation_validation_failed")


def _candidate_keys(candidates: Iterable[EvidenceCandidate]) -> set[tuple[UUID, str | None]]:
    return {(candidate.evidence_uuid, candidate.chunk_id) for candidate in candidates}


def _candidate_evidence_uuids(candidates: Iterable[EvidenceCandidate]) -> set[UUID]:
    return {candidate.evidence_uuid for candidate in candidates}


def _error(
    code: str,
    message: str,
    *,
    claim_uuid: UUID | None = None,
    evidence_uuid: UUID | None = None,
) -> EvaluationValidationError:
    return EvaluationValidationError(
        code=code,
        message=message,
        claim_uuid=claim_uuid,
        evidence_uuid=evidence_uuid,
    )


def _validate_citation(
    citation: EvidenceCitation,
    candidates: list[EvidenceCandidate],
) -> list[EvaluationValidationError]:
    errors: list[EvaluationValidationError] = []
    if citation.source_kind == EvidenceSourceKind.paper_summary:
        errors.append(
            _error(
                "summary_citation_forbidden",
                "Paper summaries are navigation only and cannot be cited as verdict evidence.",
                claim_uuid=citation.claim_uuid,
                evidence_uuid=citation.evidence_uuid,
            )
        )

    candidate_keys = _candidate_keys(candidates)
    candidate_evidence_uuids = _candidate_evidence_uuids(candidates)
    if citation.evidence_uuid not in candidate_evidence_uuids:
        errors.append(
            _error(
                "citation_outside_retrieval_set",
                "Citation evidence UUID is not in this claim's retrieval set.",
                claim_uuid=citation.claim_uuid,
                evidence_uuid=citation.evidence_uuid,
            )
        )
    elif (citation.evidence_uuid, citation.chunk_id) not in candidate_keys:
        errors.append(
            _error(
                "citation_chunk_mismatch",
                "Citation chunk ID does not match the candidate retrieval set.",
                claim_uuid=citation.claim_uuid,
                evidence_uuid=citation.evidence_uuid,
            )
        )
    return errors


def validate_claim_evaluations(
    expected_claim_uuids: Sequence[UUID],
    evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    evaluations: Sequence[ClaimEvaluation],
) -> list[EvaluationValidationError]:
    errors: list[EvaluationValidationError] = []
    expected = set(expected_claim_uuids)
    seen = [evaluation.claim_uuid for evaluation in evaluations]
    counts = Counter(seen)

    for claim_uuid in sorted(expected - set(seen), key=str):
        errors.append(
            _error(
                "missing_claim_evaluation",
                "Every expected claim must have exactly one evaluation.",
                claim_uuid=claim_uuid,
            )
        )
    for claim_uuid, count in counts.items():
        if count > 1:
            errors.append(
                _error(
                    "duplicate_claim_evaluation",
                    "Every expected claim must have exactly one evaluation.",
                    claim_uuid=claim_uuid,
                )
            )
        if claim_uuid not in expected:
            errors.append(
                _error(
                    "unexpected_claim_evaluation",
                    "Evaluation references a claim outside the expected claim set.",
                    claim_uuid=claim_uuid,
                )
            )

    for evaluation in evaluations:
        candidates = evidence_sets.get(evaluation.claim_uuid, ClaimEvidenceSet(claim_uuid=evaluation.claim_uuid)).candidates
        if evaluation.label != EvaluationLabel.insufficient and not evaluation.citations:
            errors.append(
                _error(
                    "uncited_non_insufficient_label",
                    "Supported, contradicted, and mixed labels require at least one valid citation.",
                    claim_uuid=evaluation.claim_uuid,
                )
            )
        if evaluation.label == EvaluationLabel.insufficient and not (
            evaluation.uncertainty_note or "evidence" in evaluation.rationale.lower()
        ):
            errors.append(
                _error(
                    "insufficient_missing_explanation",
                    "Insufficient labels require a concrete missing-evidence explanation.",
                    claim_uuid=evaluation.claim_uuid,
                )
            )
        for citation in evaluation.citations:
            if citation.claim_uuid != evaluation.claim_uuid:
                errors.append(
                    _error(
                        "citation_claim_mismatch",
                        "Citation claim UUID must match the evaluated claim UUID.",
                        claim_uuid=evaluation.claim_uuid,
                        evidence_uuid=citation.evidence_uuid,
                    )
                )
            errors.extend(_validate_citation(citation, candidates))

    return errors


def ensure_valid_claim_evaluations(
    expected_claim_uuids: Sequence[UUID],
    evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    evaluations: Sequence[ClaimEvaluation],
) -> None:
    errors = validate_claim_evaluations(expected_claim_uuids, evidence_sets, evaluations)
    if errors:
        raise EvaluationValidationFailure(errors)
