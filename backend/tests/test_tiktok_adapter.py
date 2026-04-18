import json

import pytest

from app.ingestion.adapters import tiktok


class FakeProcess:
    def __init__(self, stdout: bytes = b"", returncode: int = 0) -> None:
        self._stdout = stdout
        self.returncode = returncode

    async def communicate(self):
        return self._stdout, b""


def test_unsupported_url_rejected_before_subprocess(monkeypatch):
    called = False

    async def fake_create_subprocess_exec(*_args, **_kwargs):
        nonlocal called
        called = True
        return FakeProcess()

    monkeypatch.setattr(tiktok.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    assert tiktok.is_supported_tiktok_url("https://example.com/@creator/video/1") is False

    with pytest.raises(ValueError):
        import asyncio

        asyncio.run(tiktok.fetch_public_metadata("https://example.com/@creator/video/1"))

    assert called is False


def test_fetch_public_metadata_maps_title_uploader_and_id(monkeypatch):
    payload = {
        "id": "1234567890",
        "title": "Attention paper explained",
        "uploader": "ai_creator",
        "description": "arXiv:1706.03762",
    }

    async def fake_create_subprocess_exec(*_args, **_kwargs):
        return FakeProcess(json.dumps(payload).encode(), returncode=0)

    monkeypatch.setattr(tiktok.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    import asyncio

    metadata = asyncio.run(
        tiktok.fetch_public_metadata("https://www.tiktok.com/@ai_creator/video/1234567890")
    )

    assert metadata["id"] == "1234567890"
    assert metadata["title"] == "Attention paper explained"
    assert metadata["uploader"] == "ai_creator"
    assert metadata["creator_alias"] == "ai_creator"


def test_extract_subtitle_failure_returns_none(monkeypatch, tmp_path):
    async def fake_create_subprocess_exec(*args, **_kwargs):
        assert "--write-auto-subs" in args
        return FakeProcess(returncode=1)

    monkeypatch.setattr(tiktok.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    import asyncio

    result = asyncio.run(
        tiktok.extract_subtitle_file(
            "https://www.tiktok.com/@ai_creator/video/1234567890",
            tmp_path,
        )
    )

    assert result is None


def test_extract_thumbnail_file_writes_public_thumbnail(monkeypatch, tmp_path):
    async def fake_create_subprocess_exec(*args, **_kwargs):
        assert "--write-thumbnail" in args
        output_path = args[args.index("-o") + 1].replace("%(ext)s", "webp")
        from pathlib import Path

        Path(output_path).write_bytes(b"thumbnail")
        return FakeProcess(returncode=0)

    monkeypatch.setattr(tiktok.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    import asyncio

    result = asyncio.run(
        tiktok.extract_thumbnail_file(
            "https://www.tiktok.com/@ai_creator/video/1234567890",
            tmp_path,
        )
    )

    assert result is not None
    assert result.name == "thumbnail.webp"


def test_download_video_file_uses_size_limit_and_returns_download(monkeypatch, tmp_path):
    async def fake_create_subprocess_exec(*args, **_kwargs):
        assert "--max-filesize" in args
        assert "125M" in args
        output_path = args[args.index("-o") + 1].replace("%(ext)s", "mp4")
        from pathlib import Path

        Path(output_path).write_bytes(b"video")
        return FakeProcess(returncode=0)

    monkeypatch.setattr(tiktok.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

    import asyncio

    result = asyncio.run(
        tiktok.download_video_file(
            "https://www.tiktok.com/@ai_creator/video/1234567890",
            tmp_path,
            max_video_mb=125,
        )
    )

    assert result is not None
    assert result.name == "video.mp4"
