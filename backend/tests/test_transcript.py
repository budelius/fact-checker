from uuid import uuid4

from app.ingestion.transcript import (
    build_transcript_artifact,
    parse_timestamp_to_seconds,
    parse_vtt_segments,
    transcript_from_plain_text,
)
from app.schemas.ingestion import TranscriptRetrievalMethod


def test_parse_vtt_segments_preserves_timestamps():
    raw = """WEBVTT

00:00:01.000 --> 00:00:03.500
Attention scales with sequence length.

00:00:05.000 --> 00:00:06.250
arXiv:1706.03762 is the source.
"""

    segments = parse_vtt_segments(raw, TranscriptRetrievalMethod.public_caption)

    assert len(segments) == 2
    assert segments[0].start_seconds == 1.0
    assert segments[0].end_seconds == 3.5
    assert segments[1].text == "arXiv:1706.03762 is the source."


def test_parse_timestamp_accepts_srt_comma_timestamp():
    assert parse_timestamp_to_seconds("00:01:02,500") == 62.5


def test_plain_text_transcript_uses_fixture_method():
    artifact = transcript_from_plain_text(
        "A fixture transcript.",
        TranscriptRetrievalMethod.fixture,
    )

    assert artifact.provenance.method is TranscriptRetrievalMethod.fixture
    assert artifact.segments[0].start_seconds is None
    assert artifact.plain_text == "A fixture transcript."


def test_build_transcript_artifact_supports_all_methods():
    for method in (
        TranscriptRetrievalMethod.fixture,
        TranscriptRetrievalMethod.pasted,
        TranscriptRetrievalMethod.public_caption,
        TranscriptRetrievalMethod.subtitle_file,
        TranscriptRetrievalMethod.transcription,
    ):
        artifact = build_transcript_artifact(
            source_video_uuid=uuid4(),
            method=method,
            source_url="https://www.tiktok.com/@fixture/video/1234567890",
            raw_text="Plain transcript",
        )

        assert artifact.provenance.method is method
        assert artifact.segments[0].text == "Plain transcript"
