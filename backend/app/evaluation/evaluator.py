import json
from collections.abc import Mapping, Sequence
from typing import Protocol
from uuid import UUID

from openai import OpenAI

from app.evaluation.evidence import ClaimEvidenceSet
from app.evaluation.prompts import build_evaluation_prompt
from app.schemas.claims import ExtractedClaim
from app.schemas.evaluation import (
    ClaimEvaluation,
    EvaluationLabel,
    EvidenceCandidate,
    EvidenceCitation,
)
from app.settings import Settings


def _claim_uuid(claim: ExtractedClaim | dict) -> UUID:
    if isinstance(claim, ExtractedClaim):
        return claim.uuid
    return UUID(str(claim["uuid"]))


def _claim_text(claim: ExtractedClaim | dict) -> str:
    return claim.claim_text if isinstance(claim, ExtractedClaim) else str(claim["claim_text"])


def citation_from_candidate(candidate: EvidenceCandidate) -> EvidenceCitation:
    return EvidenceCitation(
        claim_uuid=candidate.claim_uuid,
        evidence_uuid=candidate.evidence_uuid,
        source_kind=candidate.source_kind,
        title=candidate.title,
        source_url=candidate.source_url,
        paper_uuid=candidate.paper_uuid,
        source_uuid=candidate.source_uuid,
        candidate_uuid=candidate.candidate_uuid,
        chunk_id=candidate.chunk_id,
        page_start=candidate.page_start,
        page_end=candidate.page_end,
        section=candidate.section,
        excerpt=candidate.excerpt or candidate.raw_text[:500],
        publication_status=candidate.publication_status,
        is_preprint=candidate.is_preprint,
        source_policy_notes=candidate.source_policy_notes,
    )


class ClaimEvaluator(Protocol):
    def evaluate(
        self,
        claims: Sequence[ExtractedClaim | dict],
        evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    ) -> list[ClaimEvaluation]:
        ...


class DeterministicEvaluator:
    def evaluate(
        self,
        claims: Sequence[ExtractedClaim | dict],
        evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    ) -> list[ClaimEvaluation]:
        evaluations: list[ClaimEvaluation] = []
        for claim in claims:
            claim_uuid = _claim_uuid(claim)
            evidence_set = evidence_sets.get(claim_uuid)
            if not evidence_set or not evidence_set.candidates:
                evaluations.append(
                    ClaimEvaluation(
                        claim_uuid=claim_uuid,
                        claim_text=_claim_text(claim),
                        label=EvaluationLabel.insufficient,
                        rationale="No direct scientific evidence was available for this claim.",
                        uncertainty_note="No selected paper chunks directly address the claim.",
                        candidate_evidence=evidence_set.candidates if evidence_set else [],
                        unused_candidate_evidence=evidence_set.unused_candidates if evidence_set else [],
                    )
                )
                continue

            citation = citation_from_candidate(evidence_set.candidates[0])
            evaluations.append(
                ClaimEvaluation(
                    claim_uuid=claim_uuid,
                    claim_text=_claim_text(claim),
                    label=EvaluationLabel.supported,
                    rationale="Deterministic evaluation cites the first selected source chunk.",
                    citations=[citation],
                    candidate_evidence=evidence_set.candidates,
                    unused_candidate_evidence=evidence_set.unused_candidates,
                    preprint_notes=(
                        ["At least one cited source is a preprint."]
                        if citation.is_preprint
                        else []
                    ),
                )
            )
        return evaluations


class FakeEvaluator(DeterministicEvaluator):
    def __init__(self, evaluations: list[ClaimEvaluation] | None = None) -> None:
        self._evaluations = evaluations

    def evaluate(
        self,
        claims: Sequence[ExtractedClaim | dict],
        evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    ) -> list[ClaimEvaluation]:
        if self._evaluations is not None:
            return list(self._evaluations)
        return super().evaluate(claims, evidence_sets)


class OpenAIClaimEvaluator:
    def __init__(self, settings: Settings, client: OpenAI | None = None) -> None:
        self.settings = settings
        self.client = client or OpenAI(api_key=settings.openai_api_key)

    def evaluate(
        self,
        claims: Sequence[ExtractedClaim | dict],
        evidence_sets: Mapping[UUID, ClaimEvidenceSet],
    ) -> list[ClaimEvaluation]:
        response = self.client.responses.create(
            model=self.settings.openai_evaluation_model,
            input=build_evaluation_prompt(claims, evidence_sets),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "claim_evaluations",
                    "schema": _evaluation_response_schema(),
                    "strict": True,
                }
            },
        )
        payload = json.loads(response.output_text)
        return [ClaimEvaluation.model_validate(item) for item in payload["evaluations"]]


def _evaluation_response_schema() -> dict:
    citation_schema = {
        "type": "object",
        "properties": {
            "claim_uuid": {"type": "string"},
            "evidence_uuid": {"type": "string"},
            "source_kind": {
                "type": "string",
                "enum": ["paper_chunk", "direct_source_text", "news_article", "paper_summary"],
            },
            "title": {"type": "string"},
            "source_url": {"type": "string"},
            "paper_uuid": {"type": ["string", "null"]},
            "source_uuid": {"type": ["string", "null"]},
            "candidate_uuid": {"type": ["string", "null"]},
            "chunk_id": {"type": ["string", "null"]},
            "page_start": {"type": ["integer", "null"]},
            "page_end": {"type": ["integer", "null"]},
            "section": {"type": ["string", "null"]},
            "excerpt": {"type": "string"},
            "publication_status": {"type": ["string", "null"]},
            "is_preprint": {"type": "boolean"},
            "source_policy_notes": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "claim_uuid",
            "evidence_uuid",
            "source_kind",
            "title",
            "source_url",
            "paper_uuid",
            "source_uuid",
            "candidate_uuid",
            "chunk_id",
            "page_start",
            "page_end",
            "section",
            "excerpt",
            "publication_status",
            "is_preprint",
            "source_policy_notes",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "evaluations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim_uuid": {"type": "string"},
                        "claim_text": {"type": "string"},
                        "label": {
                            "type": "string",
                            "enum": ["supported", "contradicted", "mixed", "insufficient"],
                        },
                        "rationale": {"type": "string"},
                        "citations": {"type": "array", "items": citation_schema},
                        "subclaims": {"type": "array", "items": {"type": "object"}},
                        "uncertainty_note": {"type": ["string", "null"]},
                        "overclaim_note": {"type": ["string", "null"]},
                        "source_limit_notes": {"type": "array", "items": {"type": "string"}},
                        "preprint_notes": {"type": "array", "items": {"type": "string"}},
                        "news_exception": {"type": "boolean"},
                    },
                    "required": [
                        "claim_uuid",
                        "claim_text",
                        "label",
                        "rationale",
                        "citations",
                        "subclaims",
                        "uncertainty_note",
                        "overclaim_note",
                        "source_limit_notes",
                        "preprint_notes",
                        "news_exception",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["evaluations"],
        "additionalProperties": False,
    }
