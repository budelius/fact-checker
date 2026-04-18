import re
from uuid import UUID, uuid4

from app.schemas.ingestion import (
    TranscriptArtifact,
    TranscriptProvenance,
    TranscriptRetrievalMethod,
    TranscriptSegment,
)

TIMING_SEPARATOR = "-->"
TAG_PATTERN = re.compile(r"<[^>]+>")


def parse_timestamp_to_seconds(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    parts = normalized.split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    elif len(parts) == 3:
        hours, minutes, seconds = parts
    else:
        raise ValueError(f"Invalid timestamp: {value}")

    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _clean_caption_line(line: str) -> str:
    return TAG_PATTERN.sub("", line).strip()


def parse_vtt_segments(raw: str, method: TranscriptRetrievalMethod) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n"))

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((i for i, line in enumerate(lines) if TIMING_SEPARATOR in line), None)
        if timing_index is None:
            continue

        start_raw, end_raw = lines[timing_index].split(TIMING_SEPARATOR, maxsplit=1)
        end_raw = end_raw.split()[0]
        text = " ".join(
            cleaned
            for cleaned in (_clean_caption_line(line) for line in lines[timing_index + 1 :])
            if cleaned
        )
        if not text:
            continue

        segments.append(
            TranscriptSegment(
                start_seconds=parse_timestamp_to_seconds(start_raw),
                end_seconds=parse_timestamp_to_seconds(end_raw),
                text=text,
            )
        )

    return segments


def transcript_from_plain_text(
    text: str,
    method: TranscriptRetrievalMethod,
) -> TranscriptArtifact:
    return TranscriptArtifact(
        video_uuid=uuid4(),
        provenance=TranscriptProvenance(method=method, source_url="fixture://plain-text"),
        segments=[TranscriptSegment(start_seconds=None, end_seconds=None, text=text)],
        plain_text=text,
    )


def build_transcript_artifact(
    source_video_uuid: UUID,
    method: TranscriptRetrievalMethod,
    source_url: str,
    raw_text: str,
    provider: str | None = None,
) -> TranscriptArtifact:
    segments = (
        parse_vtt_segments(raw_text, method)
        if TIMING_SEPARATOR in raw_text
        else [TranscriptSegment(start_seconds=None, end_seconds=None, text=raw_text)]
    )
    plain_text = "\n".join(segment.text for segment in segments)

    return TranscriptArtifact(
        video_uuid=source_video_uuid,
        provenance=TranscriptProvenance(
            method=method,
            source_url=source_url,
            provider=provider,
        ),
        segments=segments,
        plain_text=plain_text,
    )
