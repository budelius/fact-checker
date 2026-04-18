import asyncio
import builtins
import re
from pathlib import Path
from uuid import UUID

from app.contracts.vault import expected_raw_artifact_path
from app.schemas.ingestion import ScreenshotArtifact

SourceCluePattern = {
    "doi": re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE),
    "arxiv": re.compile(r"\b(arXiv:\s*\d{4}\.\d{4,5}|arxiv\.org/abs/\d{4}\.\d{4,5})", re.I),
    "url": re.compile(r"https?://\S+", re.IGNORECASE),
    "paper_phrase": re.compile(r"\b(paper|study|preprint|researchers)\b", re.IGNORECASE),
}


def score_source_clue_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in SourceCluePattern.values())


def build_screenshot_artifact(
    source_video_uuid: UUID,
    timestamp_seconds: float | None,
    slug: str,
    source_clue_text: str | None,
    vault_path: str | None = None,
    asset_url: str | None = None,
) -> ScreenshotArtifact:
    return ScreenshotArtifact(
        video_uuid=source_video_uuid,
        timestamp_seconds=timestamp_seconds,
        vault_path=vault_path or expected_raw_artifact_path("screenshots", slug, "png"),
        asset_url=asset_url,
        source_clue=score_source_clue_text(source_clue_text or ""),
        source_clue_text=source_clue_text,
    )


async def extract_frame_with_ffmpeg(
    video_path: Path,
    output_dir: Path,
    slug: str,
    timestamp_seconds: float | None = None,
) -> Path | None:
    if not video_path.exists():
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{slug}.jpg"
    timestamp = max(timestamp_seconds or 0.0, 0.0)
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-y",
        "-ss",
        f"{timestamp:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await asyncio.wait_for(process.communicate(), timeout=30)

    if process.returncode != 0 or not output_path.is_file():
        return None

    return output_path


def extract_keyframes_from_video(
    video_path: Path,
    source_video_uuid: UUID,
    max_frames: int = 10,
) -> list[ScreenshotArtifact]:
    try:
        cv2 = builtins.__import__("cv2")
    except ImportError:
        return []

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return []

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    interval = max(int(fps * 5), 1)
    frame_count = 0
    artifacts: list[ScreenshotArtifact] = []

    while len(artifacts) < max_frames:
        ok, _frame = capture.read()
        if not ok:
            break

        if frame_count % interval == 0:
            timestamp_seconds = frame_count / fps
            artifacts.append(
                build_screenshot_artifact(
                    source_video_uuid=source_video_uuid,
                    timestamp_seconds=timestamp_seconds,
                    slug=f"{video_path.stem}-frame-{len(artifacts) + 1}",
                    source_clue_text=None,
                )
            )

        frame_count += 1

    capture.release()
    return artifacts
