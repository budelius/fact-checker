import json
from uuid import uuid4

from app.ingestion.claims import build_claim_prompt, parse_claim_response
from app.schemas.claims import ClaimExtractionStatus, EvidenceStatus
from app.schemas.ingestion import (
    TranscriptArtifact,
    TranscriptProvenance,
    TranscriptRetrievalMethod,
    TranscriptSegment,
)


def _transcript_artifact() -> TranscriptArtifact:
    return TranscriptArtifact(
        video_uuid=uuid4(),
        provenance=TranscriptProvenance(
            method=TranscriptRetrievalMethod.fixture,
            source_url="https://www.tiktok.com/@fixture/video/1234567890",
        ),
        segments=[
            TranscriptSegment(
                start_seconds=1.0,
                end_seconds=3.0,
                text="A paper says transformers scale well.",
            )
        ],
        plain_text="A paper says transformers scale well.",
    )


def test_claim_prompt_wraps_untrusted_transcript():
    prompt = build_claim_prompt(_transcript_artifact(), ["arXiv:1706.03762"])

    assert "<untrusted_content>" in prompt
    assert "transcript:" in prompt
    assert "visual_context:1" in prompt


def test_parse_valid_json_returns_pending_claim():
    source_video_uuid = uuid4()
    source_transcript_uuid = uuid4()
    raw = json.dumps(
        [
            {
                "claim_text": "Transformers scale well for sequence modeling.",
                "transcript_excerpt": "transformers scale well",
                "timestamp_start_seconds": 1.0,
                "timestamp_end_seconds": 3.0,
                "screenshot_uuids": [],
                "extraction_confidence": 0.84,
            }
        ]
    )

    result = parse_claim_response(raw, source_video_uuid, source_transcript_uuid)

    assert result.status is ClaimExtractionStatus.succeeded
    assert len(result.claims) == 1
    assert result.claims[0].source_video_uuid == source_video_uuid
    assert result.claims[0].evidence_status is EvidenceStatus.pending


def test_parse_invalid_json_returns_failed_without_claims():
    result = parse_claim_response("not json", uuid4(), uuid4())

    assert result.status is ClaimExtractionStatus.failed
    assert result.claims == []
    assert result.error_message is not None
    assert result.error_message.startswith("claim_extraction_parse_failed")
