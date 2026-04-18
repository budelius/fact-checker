import json
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, ValidationError

from app.safety.input_boundaries import wrap_untrusted_text
from app.schemas.claims import ClaimExtractionStatus, ExtractedClaim
from app.schemas.ingestion import TranscriptArtifact


class ClaimExtractionResult(BaseModel):
    status: ClaimExtractionStatus
    claims: list[ExtractedClaim]
    error_message: str | None = None
    raw_response: str | None = None


class ClaimExtractionProvider(Protocol):
    async def extract_claims(self, prompt: str) -> str:
        raise NotImplementedError


def build_claim_prompt(transcript: TranscriptArtifact, visual_text: list[str]) -> str:
    transcript_context = wrap_untrusted_text(
        label=f"transcript:{transcript.transcript_uuid}",
        content=transcript.plain_text,
    )
    visual_context = [
        wrap_untrusted_text(label=f"visual_context:{index}", content=text)
        for index, text in enumerate(visual_text, start=1)
    ]

    return "\n\n".join(
        [
            "Extract atomic AI research claims as JSON. Do not evaluate evidence.",
            transcript_context,
            *visual_context,
        ]
    )


def parse_claim_response(
    raw: str,
    source_video_uuid: UUID,
    source_transcript_uuid: UUID,
) -> ClaimExtractionResult:
    try:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError("expected_json_array")

        claims = [
            ExtractedClaim(
                source_video_uuid=source_video_uuid,
                source_transcript_uuid=source_transcript_uuid,
                **item,
            )
            for item in payload
        ]
    except (json.JSONDecodeError, TypeError, ValueError, ValidationError) as exc:
        return ClaimExtractionResult(
            status=ClaimExtractionStatus.failed,
            claims=[],
            error_message=f"claim_extraction_parse_failed: {exc}",
            raw_response=raw,
        )

    return ClaimExtractionResult(
        status=ClaimExtractionStatus.succeeded,
        claims=claims,
        raw_response=raw,
    )
