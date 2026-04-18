import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from pydantic import BaseModel

from app.contracts.vault import expected_raw_artifact_path

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}
ALLOWED_VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
    "application/octet-stream",
}


class UploadedVideoArtifact(BaseModel):
    media_uuid: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    raw_path: str
    provider_upload: bool = False


def slugify_filename(filename: str) -> str:
    stem = Path(filename).stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "uploaded-video"


def validate_video_upload(
    filename: str,
    content_type: str | None,
    size_bytes: int,
    max_video_mb: int,
) -> None:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValueError("unsupported_video_upload_type")
    if content_type and content_type not in ALLOWED_VIDEO_CONTENT_TYPES:
        raise ValueError("unsupported_video_upload_type")
    if size_bytes > max_video_mb * 1024 * 1024:
        raise ValueError("uploaded_video_too_large")


async def store_uploaded_video(
    upload: UploadFile,
    vault_root: Path,
    max_video_mb: int,
) -> UploadedVideoArtifact:
    data = await upload.read()
    filename = upload.filename or "uploaded-video.mp4"
    validate_video_upload(filename, upload.content_type, len(data), max_video_mb)

    media_uuid = str(uuid4())
    extension = Path(filename).suffix.lower().lstrip(".")
    slug = f"{slugify_filename(filename)}-{media_uuid[:8]}"
    raw_path = expected_raw_artifact_path("videos", slug, extension)
    absolute_path = vault_root.parent / raw_path if vault_root.name == "vault" else Path(raw_path)
    if not absolute_path.is_absolute():
        absolute_path = Path.cwd().parent / raw_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_bytes(data)

    return UploadedVideoArtifact(
        media_uuid=media_uuid,
        original_filename=filename,
        content_type=upload.content_type,
        size_bytes=len(data),
        raw_path=raw_path,
    )
