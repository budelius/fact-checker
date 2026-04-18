from pydantic import BaseModel


class MediaComplianceDecision(BaseModel):
    allowed: bool
    reason: str
    max_video_mb: int
    download_attempted: bool = False


def decide_media_download(enabled: bool, max_video_mb: int) -> MediaComplianceDecision:
    if not enabled:
        return MediaComplianceDecision(
            allowed=False,
            reason="media_download_disabled",
            max_video_mb=max_video_mb,
            download_attempted=False,
        )

    return MediaComplianceDecision(
        allowed=True,
        reason="media_download_enabled",
        max_video_mb=max_video_mb,
        download_attempted=False,
    )
