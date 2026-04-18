from uuid import uuid4

import pytest

from app.evaluation.evidence import ClaimEvidenceSet
from app.evaluation.evaluator import citation_from_candidate
from app.evaluation.validation import (
    EvaluationValidationFailure,
    ensure_valid_claim_evaluations,
    validate_claim_evaluations,
)
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationLabel,
    EvidenceCandidate,
    EvidenceCitation,
    EvidenceSourceKind,
)


def _candidate(claim_uuid) -> EvidenceCandidate:
    return EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=uuid4(),
        title="Attention Is All You Need",
        raw_text="The Transformer allows significantly more parallelization.",
        source_url="https://arxiv.org/abs/1706.03762",
        chunk_id="chunk-1",
    )


def _supported(claim_uuid, candidate) -> ClaimEvaluation:
    return ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="Transformers parallelize sequence modeling.",
        label=EvaluationLabel.supported,
        rationale="The cited chunk supports the claim.",
        citations=[citation_from_candidate(candidate)],
    )


def test_validator_accepts_cited_supported_label():
    claim_uuid = uuid4()
    candidate = _candidate(claim_uuid)
    errors = validate_claim_evaluations(
        [claim_uuid],
        {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid, candidates=[candidate])},
        [_supported(claim_uuid, candidate)],
    )

    assert errors == []


@pytest.mark.parametrize(
    "label",
    [EvaluationLabel.supported, EvaluationLabel.contradicted, EvaluationLabel.mixed],
)
def test_validator_rejects_non_insufficient_labels_without_citations(label):
    claim_uuid = uuid4()
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="A claim.",
        label=label,
        rationale="No citations.",
    )

    errors = validate_claim_evaluations(
        [claim_uuid],
        {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid)},
        [evaluation],
    )

    assert errors[0].code == "uncited_non_insufficient_label"


def test_validator_rejects_citations_outside_retrieval_set():
    claim_uuid = uuid4()
    candidate = _candidate(claim_uuid)
    outside = _candidate(claim_uuid)
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="A claim.",
        label=EvaluationLabel.supported,
        rationale="Cites the wrong evidence.",
        citations=[citation_from_candidate(outside)],
    )

    errors = validate_claim_evaluations(
        [claim_uuid],
        {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid, candidates=[candidate])},
        [evaluation],
    )

    assert errors[0].code == "citation_outside_retrieval_set"


def test_validator_rejects_duplicate_and_missing_claim_evaluations():
    first_claim_uuid = uuid4()
    second_claim_uuid = uuid4()
    candidate = _candidate(first_claim_uuid)
    evaluation = _supported(first_claim_uuid, candidate)

    errors = validate_claim_evaluations(
        [first_claim_uuid, second_claim_uuid],
        {first_claim_uuid: ClaimEvidenceSet(claim_uuid=first_claim_uuid, candidates=[candidate])},
        [evaluation, evaluation],
    )
    codes = {error.code for error in errors}

    assert "duplicate_claim_evaluation" in codes
    assert "missing_claim_evaluation" in codes


def test_validator_rejects_summary_citations():
    claim_uuid = uuid4()
    candidate = _candidate(claim_uuid)
    citation = EvidenceCitation(
        claim_uuid=claim_uuid,
        evidence_uuid=candidate.evidence_uuid,
        source_kind=EvidenceSourceKind.paper_summary,
        title="Generated summary",
        source_url="vault/wiki/papers/summary.md",
        chunk_id=candidate.chunk_id,
        excerpt="Generated summary text.",
    )
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="A claim.",
        label=EvaluationLabel.supported,
        rationale="Cites a summary.",
        citations=[citation],
    )

    errors = validate_claim_evaluations(
        [claim_uuid],
        {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid, candidates=[candidate])},
        [evaluation],
    )

    assert {error.code for error in errors} >= {"summary_citation_forbidden"}


def test_validator_accepts_insufficient_without_citations_when_explained():
    claim_uuid = uuid4()
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="A claim.",
        label=EvaluationLabel.insufficient,
        rationale="No direct evidence addressed the claim.",
        uncertainty_note="The selected papers do not discuss this claim.",
    )

    ensure_valid_claim_evaluations(
        [claim_uuid],
        {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid)},
        [evaluation],
    )


def test_ensure_valid_raises_with_typed_errors():
    claim_uuid = uuid4()
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="A claim.",
        label=EvaluationLabel.mixed,
        rationale="No citations.",
    )

    with pytest.raises(EvaluationValidationFailure) as caught:
        ensure_valid_claim_evaluations(
            [claim_uuid],
            {claim_uuid: ClaimEvidenceSet(claim_uuid=claim_uuid)},
            [evaluation],
        )

    assert caught.value.errors[0].code == "uncited_non_insufficient_label"
