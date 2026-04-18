from collections.abc import Mapping, Sequence
from uuid import UUID

from app.evaluation.evidence import ClaimEvidenceSet
from app.safety.input_boundaries import wrap_untrusted_text
from app.schemas.claims import ExtractedClaim


def _claim_uuid(claim: ExtractedClaim | dict) -> UUID:
    if isinstance(claim, ExtractedClaim):
        return claim.uuid
    return UUID(str(claim["uuid"]))


def _claim_text(claim: ExtractedClaim | dict) -> str:
    return claim.claim_text if isinstance(claim, ExtractedClaim) else str(claim["claim_text"])


def _transcript_excerpt(claim: ExtractedClaim | dict) -> str:
    if isinstance(claim, ExtractedClaim):
        return claim.transcript_excerpt
    return str(claim.get("transcript_excerpt") or "")


def build_evaluation_prompt(
    claims: Sequence[ExtractedClaim | dict],
    evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    *,
    screenshot_context_by_claim: Mapping[UUID, Sequence[str]] | None = None,
) -> str:
    screenshot_context_by_claim = screenshot_context_by_claim or {}
    sections = [
        "Evaluate AI research claims against the provided source evidence.",
        "Return strict JSON only.",
        "Labels must be exactly: supported, contradicted, mixed, insufficient.",
        "Be creative in analysis but conservative in verdicts.",
        "Decompose compound claims into subclaims and penalize overclaiming.",
        "Use supported only when direct evidence supports the claim's main idea and scope.",
        "Use mixed when some important subclaims, scope, or qualifiers are not supported.",
        "Use contradicted when direct source evidence conflicts with the claim.",
        "Use insufficient when direct evidence is missing, adjacent, ambiguous, or too weak.",
        "Paper summaries are navigation only and were not used as verdict evidence.",
        "Cite only evidence chunks or direct source text provided below.",
        "Do not cite generated summaries, transcript text, screenshots, captions, or comments.",
        "Mark preprint and source limitation notes when relevant.",
        "The rare news exception is allowed only when the claim is specifically about a news article.",
    ]

    for claim in claims:
        claim_uuid = _claim_uuid(claim)
        evidence_set = evidence_sets.get(claim_uuid)
        sections.append(f"\n## Claim {claim_uuid}")
        sections.append(wrap_untrusted_text(f"claim:{claim_uuid}", _claim_text(claim)))
        sections.append(
            wrap_untrusted_text(
                f"transcript_excerpt:{claim_uuid}",
                _transcript_excerpt(claim) or "No transcript excerpt available.",
            )
        )
        for index, screenshot_text in enumerate(screenshot_context_by_claim.get(claim_uuid, []), start=1):
            sections.append(
                wrap_untrusted_text(f"screenshot_context:{claim_uuid}:{index}", screenshot_text)
            )
        if not evidence_set or not evidence_set.candidates:
            sections.append(
                "No direct scientific evidence chunks were provided for this claim. "
                "The label should be insufficient unless a valid news exception is present."
            )
            continue
        for candidate in evidence_set.candidates:
            label = f"evidence:{claim_uuid}:{candidate.evidence_uuid}:{candidate.chunk_id or 'direct'}"
            sections.append(
                "\n".join(
                    [
                        f"Evidence UUID: {candidate.evidence_uuid}",
                        f"Source kind: {candidate.source_kind.value}",
                        f"Title: {candidate.title}",
                        f"Source URL: {candidate.source_url}",
                        f"Chunk ID: {candidate.chunk_id or 'direct'}",
                        f"Publication status: {candidate.publication_status or 'unknown'}",
                        wrap_untrusted_text(label, candidate.raw_text),
                    ]
                )
            )

    return "\n\n".join(sections)
