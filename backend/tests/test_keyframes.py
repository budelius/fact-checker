import builtins
from uuid import uuid4

from app.ingestion.keyframes import (
    build_screenshot_artifact,
    extract_keyframes_from_video,
    score_source_clue_text,
)


def test_source_clue_detects_doi_arxiv_and_url():
    assert score_source_clue_text("DOI 10.1145/1234567")
    assert score_source_clue_text("See arxiv.org/abs/1706.03762")
    assert score_source_clue_text("Source: https://example.com/paper")
    assert score_source_clue_text("The paper reports a benchmark.")


def test_build_screenshot_artifact_sets_uuid_path_and_source_clue():
    video_uuid = uuid4()
    artifact = build_screenshot_artifact(
        source_video_uuid=video_uuid,
        timestamp_seconds=12.5,
        slug="attention-slide",
        source_clue_text="arXiv:1706.03762",
    )

    assert artifact.video_uuid == video_uuid
    assert artifact.vault_path == "vault/raw/screenshots/attention-slide.png"
    assert artifact.source_clue is True


def test_extract_keyframes_missing_cv2_returns_empty_list(monkeypatch, tmp_path):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "cv2":
            raise ImportError("cv2 missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    assert extract_keyframes_from_video(tmp_path / "fixture.mp4", uuid4()) == []
