import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from app.ingestion.compliance import MediaComplianceDecision
from app.schemas.ingestion import TranscriptArtifact


class TikTokAdapterResult(BaseModel):
    source_url: str
    external_video_id: str | None = None
    creator_alias: str | None = None
    title: str | None = None
    description: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    transcript_artifact: TranscriptArtifact | None = None
    media_decision: MediaComplianceDecision | None = None
    media_path: str | None = None
    errors: list[str] = Field(default_factory=list)


def is_supported_tiktok_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = (parsed.hostname or "").lower().rstrip(".")
    return hostname == "tiktok.com" or hostname.endswith(".tiktok.com")


async def fetch_public_metadata(url: str) -> dict[str, object]:
    if not is_supported_tiktok_url(url):
        raise ValueError("unsupported_tiktok_url")

    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--no-playlist",
        "--dump-json",
        "--no-download",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _stderr = await asyncio.wait_for(process.communicate(), timeout=30)

    if process.returncode != 0 or not stdout:
        return {}

    try:
        data = json.loads(stdout.decode(errors="replace"))
    except json.JSONDecodeError:
        return {}

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "uploader": data.get("uploader"),
        "creator_alias": data.get("uploader") or data.get("channel"),
        "description": data.get("description"),
        "raw": data,
    }


async def extract_subtitle_file(url: str, output_dir: Path) -> Path | None:
    if not is_supported_tiktok_url(url):
        raise ValueError("unsupported_tiktok_url")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = output_dir / "subs.%(ext)s"
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--no-playlist",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "en.*,en",
        "--sub-format",
        "json3/srv3/vtt/srt/best",
        "--convert-subs",
        "vtt",
        "-o",
        str(output_template),
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await asyncio.wait_for(process.communicate(), timeout=60)

    if process.returncode != 0:
        return None

    candidates = sorted(
        list(output_dir.glob("*.vtt"))
        + list(output_dir.glob("*.srt"))
        + list(output_dir.glob("*.json3"))
    )
    return candidates[0] if candidates else None
