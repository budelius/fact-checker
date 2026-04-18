from tempfile import TemporaryDirectory
from pathlib import Path
import shutil
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.contracts.vault import VAULT_RAW_ARTIFACT_FOLDERS, expected_raw_artifact_path
from app.ingestion.adapters.tiktok import (
    download_video_file,
    extract_subtitle_file,
    extract_thumbnail_file,
    fetch_public_metadata,
    is_supported_tiktok_url,
)
from app.ingestion.claims import extract_fixture_claims
from app.ingestion.compliance import decide_media_download
from app.ingestion.jobs import create_ingestion_job, get_job, mark_job_succeeded, save_job, serialize_job
from app.ingestion.keyframes import (
    build_screenshot_artifact,
    extract_frame_with_ffmpeg,
    score_source_clue_text,
)
from app.ingestion.research_basis import triage_research_basis
from app.ingestion.transcript import build_transcript_artifact
from app.ingestion.uploads import store_uploaded_video
from app.schemas.ingestion import (
    ArtifactStatus,
    ArtifactType,
    IngestionJob,
    IngestionStageName,
    JobLifecycleStatus,
    SourceKind,
    StageStatus,
    TranscriptArtifact,
    TranscriptRetrievalMethod,
)
from app.settings import get_settings

from app.ingestion.progress import update_stage


router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class TikTokSubmitRequest(BaseModel):
    url: str


class PastedTranscriptRequest(BaseModel):
    source_url: str
    transcript: str
    title: str | None = None


def _add_artifact(
    job: IngestionJob,
    artifact_type: ArtifactType,
    status: StageStatus,
    label: str,
    message: str = "",
    details: dict | None = None,
    entity_uuid: UUID | None = None,
) -> None:
    job.artifacts.append(
        ArtifactStatus(
            artifact_type=artifact_type,
            status=status,
            label=label,
            message=message,
            details=details or {},
            entity_uuid=entity_uuid,
        )
    )


def _candidate_summary(candidate_count: int) -> str:
    if candidate_count:
        return f"Claims extracted and {candidate_count} source candidates ready for paper discovery."
    return "Claims extracted; no paper or source references found in transcript or screenshots."


def _asset_url_for_vault_path(vault_path: str) -> str | None:
    prefix = "vault/raw/"
    if not vault_path.startswith(prefix):
        return None

    remainder = vault_path[len(prefix) :]
    if "/" not in remainder:
        return None

    kind, filename = remainder.split("/", 1)
    if kind not in VAULT_RAW_ARTIFACT_FOLDERS or "/" in filename or "\\" in filename:
        return None

    return f"/ingestion/artifacts/raw/{kind}/{filename}"


def _image_suffix(source_file: Path) -> str:
    with source_file.open("rb") as handle:
        header = handle.read(16)

    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"

    suffix = source_file.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return ".jpg"


def _store_screenshot_asset(source_file: Path, slug: str) -> tuple[str, str] | None:
    if not source_file.exists():
        return None

    suffix = _image_suffix(source_file)
    settings = get_settings()
    destination_dir = Path(settings.vault_root) / "raw" / "screenshots"
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / f"{slug}{suffix}"
    shutil.copyfile(source_file, destination)
    vault_path = expected_raw_artifact_path("screenshots", slug, suffix)
    asset_url = _asset_url_for_vault_path(vault_path)
    return (vault_path, asset_url) if asset_url else None


def _source_clue_context(transcript: TranscriptArtifact) -> tuple[float | None, str | None]:
    for segment in transcript.segments:
        if score_source_clue_text(segment.text):
            return segment.start_seconds, segment.text

    if score_source_clue_text(transcript.plain_text):
        return (
            transcript.segments[0].start_seconds if transcript.segments else None,
            transcript.plain_text[:240],
        )

    return (
        transcript.segments[0].start_seconds if transcript.segments else None,
        None,
    )


def _build_screenshot_clues(
    job: IngestionJob,
    transcript: TranscriptArtifact,
    preview_file: Path | None = None,
):
    screenshots = []
    timestamp_seconds, source_clue_text = _source_clue_context(transcript)
    has_source_clue = source_clue_text is not None and score_source_clue_text(source_clue_text)
    if has_source_clue or preview_file is not None:
        slug = f"{job.job_uuid}-source-clue"
        stored_asset = _store_screenshot_asset(preview_file, slug) if preview_file else None
        vault_path, asset_url = stored_asset if stored_asset else (None, None)
        screenshots.append(
            build_screenshot_artifact(
                source_video_uuid=transcript.video_uuid,
                timestamp_seconds=timestamp_seconds,
                slug=slug,
                source_clue_text=source_clue_text,
                vault_path=vault_path,
                asset_url=asset_url,
            )
        )
    return screenshots


def _complete_transcript_job(
    job: IngestionJob,
    transcript: TranscriptArtifact,
    public_metadata: dict | None = None,
    media_artifact_details: dict | None = None,
    preview_file: Path | None = None,
) -> dict:
    job.video_uuid = transcript.video_uuid

    update_stage(job, IngestionStageName.validate_url, StageStatus.succeeded, "Input accepted.")
    update_stage(
        job,
        IngestionStageName.read_public_metadata,
        StageStatus.succeeded if public_metadata else StageStatus.skipped,
        "Public metadata normalized." if public_metadata else "Public metadata skipped for local fixture.",
    )
    update_stage(
        job,
        IngestionStageName.build_transcript,
        StageStatus.succeeded,
        "Transcript artifact created.",
        transcript.transcript_uuid,
    )

    screenshots = _build_screenshot_clues(job, transcript, preview_file)
    update_stage(
        job,
        IngestionStageName.capture_source_clues,
        StageStatus.succeeded if screenshots else StageStatus.skipped,
        "Source-clue screenshot artifacts created." if screenshots else "No source-clue frames captured yet.",
    )

    claim_result = extract_fixture_claims(transcript)
    claims = claim_result.claims
    update_stage(
        job,
        IngestionStageName.extract_claims,
        StageStatus.succeeded if claims else StageStatus.skipped,
        "Claims extracted with local fixture extractor." if claims else "claim_extraction_provider_disabled",
    )

    triage = triage_research_basis(transcript, screenshots)
    for claim in claims:
        claim.source_candidate_count = triage.candidate_count

    update_stage(
        job,
        IngestionStageName.triage_research_basis,
        StageStatus.succeeded,
        triage.reason,
    )
    update_stage(
        job,
        IngestionStageName.write_owned_artifacts,
        StageStatus.succeeded,
        "Owned Phase 2 artifacts normalized for persistence.",
    )

    if media_artifact_details:
        _add_artifact(
            job,
            ArtifactType.media_retrieval,
            StageStatus.succeeded,
            "Media retrieval",
            "Uploaded video stored locally.",
            media_artifact_details,
        )

    if public_metadata:
        _add_artifact(
            job,
            ArtifactType.public_metadata,
            StageStatus.succeeded,
            "Public metadata",
            "Public metadata retrieved.",
            _metadata_details(job.source_url, public_metadata),
        )

    _add_artifact(
        job,
        ArtifactType.transcript,
        StageStatus.succeeded,
        "Transcript",
        "Transcript ready.",
        {
            "method": transcript.provenance.method.value,
            "segment_count": len(transcript.segments),
            "source_url": transcript.provenance.source_url,
        },
        transcript.transcript_uuid,
    )
    _add_artifact(
        job,
        ArtifactType.screenshot,
        StageStatus.succeeded if screenshots else StageStatus.skipped,
        "Screenshots/keyframes",
        "Source-clue screenshots ready." if screenshots else "No source-clue frames captured yet.",
        {"count": len(screenshots)},
    )
    _add_artifact(
        job,
        ArtifactType.claims,
        StageStatus.succeeded if claims else StageStatus.skipped,
        "Claims",
        f"{len(claims)} claims extracted." if claims else "No claims extracted.",
        {"count": len(claims)},
    )
    _add_artifact(
        job,
        ArtifactType.research_basis,
        StageStatus.succeeded,
        "Research basis",
        triage.reason,
        {"status": triage.status.value, "candidate_count": triage.candidate_count},
    )

    mark_job_succeeded(job, _candidate_summary(triage.candidate_count))
    research_basis_payload = triage.model_dump(mode="json")
    research_basis_payload["candidate_count"] = triage.candidate_count

    return save_job(
        serialize_job(
            job,
            public_metadata=_metadata_details(job.source_url, public_metadata) if public_metadata else {},
            transcript_artifact=transcript,
            screenshots=screenshots,
            claims=claims,
            research_basis=research_basis_payload,
        )
    )


def _metadata_details(source_url: str, metadata: dict[str, object]) -> dict[str, object]:
    return {
        "source_url": source_url,
        "external_video_id": metadata.get("id"),
        "creator_alias": metadata.get("creator_alias") or metadata.get("uploader"),
        "title": metadata.get("title"),
        "description": metadata.get("description"),
    }


@router.post("/tiktok")
async def submit_tiktok_url(request: TikTokSubmitRequest) -> dict:
    if not is_supported_tiktok_url(request.url):
        raise HTTPException(status_code=400, detail="unsupported_tiktok_url")

    job = create_ingestion_job(request.url, SourceKind.tiktok_url)
    update_stage(job, IngestionStageName.validate_url, StageStatus.succeeded, "Public TikTok URL accepted.")
    update_stage(job, IngestionStageName.read_public_metadata, StageStatus.running, "Reading public metadata.")
    try:
        metadata = await fetch_public_metadata(request.url)
    except Exception as exc:
        metadata = {}
        update_stage(
            job,
            IngestionStageName.read_public_metadata,
            StageStatus.failed,
            f"Public metadata retrieval failed: {type(exc).__name__}",
        )
    else:
        update_stage(
            job,
            IngestionStageName.read_public_metadata,
            StageStatus.succeeded if metadata else StageStatus.failed,
            "Public metadata retrieved." if metadata else "Public metadata unavailable.",
        )

    update_stage(job, IngestionStageName.build_transcript, StageStatus.running, "Reading captions.")
    transcript = None
    with TemporaryDirectory(prefix="fact-checker-subs-") as output_dir:
        output_path = Path(output_dir)
        subtitle_file = await extract_subtitle_file(request.url, output_path)
        if subtitle_file is not None:
            transcript = build_transcript_artifact(
                source_video_uuid=job.video_uuid or uuid4(),
                method=TranscriptRetrievalMethod.subtitle_file,
                source_url=request.url,
                raw_text=subtitle_file.read_text(encoding="utf-8", errors="replace"),
                provider="yt-dlp",
            )

        preview_file = None
        if transcript is not None:
            timestamp_seconds, _source_clue_text = _source_clue_context(transcript)
            settings = get_settings()
            media_decision = decide_media_download(
                enabled=settings.tiktok_media_download_enabled,
                max_video_mb=settings.tiktok_max_video_mb,
            )
            if media_decision.allowed:
                video_file = await download_video_file(
                    request.url,
                    output_path,
                    settings.tiktok_max_video_mb,
                )
                if video_file is not None:
                    preview_file = await extract_frame_with_ffmpeg(
                        video_file,
                        output_path,
                        "source-clue-frame",
                        timestamp_seconds,
                    )

        try:
            thumbnail_file = await extract_thumbnail_file(request.url, output_path)
        except Exception:
            thumbnail_file = None

        if transcript is not None:
            return _complete_transcript_job(
                job,
                transcript,
                public_metadata=metadata,
                preview_file=preview_file or thumbnail_file,
            )

    update_stage(
        job,
        IngestionStageName.build_transcript,
        StageStatus.failed,
        "Captions unavailable. Claim extraction needs a transcript.",
    )
    job.status = JobLifecycleStatus.pending
    job.current_operation = (
        "Public metadata retrieved. Add a pasted transcript to run local claim extraction."
        if metadata
        else "URL accepted, but public metadata was unavailable. Add a pasted transcript to run locally."
    )
    metadata_details = _metadata_details(request.url, metadata)
    _add_artifact(
        job,
        ArtifactType.public_metadata,
        StageStatus.succeeded if metadata else StageStatus.failed,
        "Public metadata",
        "Public metadata retrieved." if metadata else "Public metadata unavailable.",
        metadata_details,
    )
    return save_job(
        serialize_job(
            job,
            public_metadata=metadata_details,
            transcript_artifact=None,
            screenshots=[],
            claims=[],
        )
    )


@router.post("/fixtures/transcript")
def submit_fixture_transcript(request: PastedTranscriptRequest) -> dict:
    # Fixture transcripts can include source hints such as arXiv:1706.03762.
    job = create_ingestion_job(request.source_url, SourceKind.fixture_transcript)
    video_uuid = uuid4()
    transcript = build_transcript_artifact(
        source_video_uuid=video_uuid,
        method=TranscriptRetrievalMethod.fixture,
        source_url=request.source_url,
        raw_text=request.transcript,
        provider="local_fixture",
    )
    public_metadata = {"title": request.title} if request.title else {}
    return _complete_transcript_job(job, transcript, public_metadata=public_metadata)


@router.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    transcript: str | None = Form(default=None),
) -> dict:
    settings = get_settings()
    try:
        media_artifact = await store_uploaded_video(
            upload=file,
            vault_root=Path(settings.vault_root),
            max_video_mb=settings.tiktok_max_video_mb,
        )
    except ValueError as exc:
        detail = "unsupported_upload_type"
        if str(exc) == "uploaded_video_too_large":
            detail = "upload_too_large"
        raise HTTPException(status_code=400, detail=detail) from exc

    job = create_ingestion_job(f"uploaded://{file.filename}", SourceKind.uploaded_video)
    media_details = {
        "vault_path": media_artifact.raw_path,
        "filename": media_artifact.original_filename,
        "content_type": media_artifact.content_type,
        "bytes": media_artifact.size_bytes,
        "third_party_upload": media_artifact.provider_upload,
    }

    if transcript and transcript.strip():
        transcript_artifact = build_transcript_artifact(
            source_video_uuid=uuid4(),
            method=TranscriptRetrievalMethod.pasted,
            source_url=f"uploaded://{file.filename}",
            raw_text=transcript,
            provider="local_upload",
        )
        return _complete_transcript_job(job, transcript_artifact, media_artifact_details=media_details)

    update_stage(job, IngestionStageName.validate_url, StageStatus.succeeded, "Uploaded video accepted.")
    update_stage(
        job,
        IngestionStageName.read_public_metadata,
        StageStatus.skipped,
        "Public metadata skipped for uploaded video.",
    )
    update_stage(
        job,
        IngestionStageName.build_transcript,
        StageStatus.skipped,
        "Transcript unavailable. Add pasted transcript text to run local extraction.",
    )
    update_stage(
        job,
        IngestionStageName.capture_source_clues,
        StageStatus.skipped,
        "No source-clue frames captured yet.",
    )
    update_stage(
        job,
        IngestionStageName.extract_claims,
        StageStatus.skipped,
        "claim_extraction_provider_disabled",
    )
    update_stage(
        job,
        IngestionStageName.triage_research_basis,
        StageStatus.skipped,
        "No transcript available for research-basis triage.",
    )
    update_stage(
        job,
        IngestionStageName.write_owned_artifacts,
        StageStatus.succeeded,
        "Uploaded video artifact stored locally.",
    )
    mark_job_succeeded(job, "Uploaded video stored locally. Transcript unavailable.")
    _add_artifact(
        job,
        ArtifactType.media_retrieval,
        StageStatus.succeeded,
        "Media retrieval",
        "Uploaded video stored locally.",
        media_details,
    )
    return save_job(
        serialize_job(job, public_metadata={}, transcript_artifact=None, screenshots=[], claims=[])
    )


@router.get("/jobs/{job_uuid}")
def get_ingestion_job(job_uuid: UUID) -> dict:
    job = get_job(job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="ingestion_job_not_found")
    return job


@router.get("/artifacts/raw/{kind}/{filename}")
def get_raw_artifact(kind: str, filename: str):
    if kind not in VAULT_RAW_ARTIFACT_FOLDERS or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=404, detail="raw_artifact_not_found")

    artifact_path = Path(get_settings().vault_root) / "raw" / kind / filename
    if not artifact_path.is_file():
        raise HTTPException(status_code=404, detail="raw_artifact_not_found")

    return FileResponse(artifact_path)
