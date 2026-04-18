from uuid import UUID

from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    PaperCandidate,
    SourceDecision,
)

NO_SCIENTIFIC_EVIDENCE_REASON = "no_scientific_evidence_found_for_now"


def _has_stable_identifier(candidate: PaperCandidate) -> bool:
    return bool(candidate.external_ids or any(path.url for path in candidate.discovery_paths))


def _confidence(candidate: PaperCandidate) -> float:
    return candidate.confidence if candidate.confidence is not None else 0.0


def select_ground_truth_for_claim(
    claim_uuid: UUID,
    candidates: list[PaperCandidate],
) -> list[SourceDecision]:
    decisions: list[SourceDecision] = []
    selected = False

    for candidate in candidates:
        if candidate.kind == CandidateKind.non_paper:
            candidate.status = CandidateStatus.supplemental
            decisions.append(
                SourceDecision(
                    claim_uuid=claim_uuid,
                    candidate_uuid=candidate.uuid,
                    status=CandidateStatus.supplemental,
                    reason="non_paper_source_not_v1_ground_truth",
                    provenance={"candidate_title": candidate.title},
                )
            )
            continue

        if candidate.kind not in {CandidateKind.paper, CandidateKind.preprint}:
            candidate.status = CandidateStatus.rejected
            decisions.append(
                SourceDecision(
                    claim_uuid=claim_uuid,
                    candidate_uuid=candidate.uuid,
                    status=CandidateStatus.rejected,
                    reason="wrong_paper",
                    provenance={"candidate_title": candidate.title},
                )
            )
            continue

        if not _has_stable_identifier(candidate):
            reason = "missing_stable_identifier"
            status = CandidateStatus.rejected
        elif _confidence(candidate) < 0.55:
            reason = "weak_match"
            status = CandidateStatus.rejected
        else:
            reason = "paper_or_preprint_selected"
            status = CandidateStatus.selected_ground_truth
            selected = True

        candidate.status = status
        decisions.append(
            SourceDecision(
                claim_uuid=claim_uuid,
                candidate_uuid=candidate.uuid,
                status=status,
                reason=reason,
                provenance={
                    "candidate_title": candidate.title,
                    "confidence": candidate.confidence,
                    "kind": candidate.kind.value,
                },
            )
        )

    if not selected:
        decisions.append(
            SourceDecision(
                claim_uuid=claim_uuid,
                status=CandidateStatus.no_paper_found,
                reason=NO_SCIENTIFIC_EVIDENCE_REASON,
                provenance={"candidate_count": len(candidates)},
            )
        )

    return decisions
