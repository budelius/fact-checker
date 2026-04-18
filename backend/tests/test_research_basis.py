from uuid import uuid4

from app.ingestion.research_basis import (
    extract_research_basis_candidates,
    triage_research_basis,
)
from app.schemas.ingestion import (
    ResearchBasisStatus,
    ScreenshotArtifact,
    TranscriptArtifact,
    TranscriptProvenance,
    TranscriptRetrievalMethod,
    TranscriptSegment,
)


def _transcript(text: str) -> TranscriptArtifact:
    return TranscriptArtifact(
        video_uuid=uuid4(),
        provenance=TranscriptProvenance(
            method=TranscriptRetrievalMethod.fixture,
            source_url="https://www.tiktok.com/@fixture/video/1234567890",
        ),
        segments=[TranscriptSegment(text=text)],
        plain_text=text,
    )


def test_doi_arxiv_and_url_candidates():
    transcript = _transcript(
        "The paper cites DOI 10.1145/1234567 and arXiv:1706.03762 at https://arxiv.org/abs/1706.03762"
    )

    candidates = extract_research_basis_candidates(transcript, [])
    candidate_types = {candidate.candidate_type for candidate in candidates}

    assert {"doi", "arxiv", "url", "paper_title"}.issubset(candidate_types)
    assert all(candidate.source == "transcript" for candidate in candidates)
    assert all(candidate.source_uuid == transcript.transcript_uuid for candidate in candidates)


def test_no_candidates_returns_opinion_or_unratable():
    triage = triage_research_basis(_transcript("I think AI will change work."), [])

    assert triage.status is ResearchBasisStatus.opinion_or_unratable
    assert triage.candidates == []


def test_source_clue_screenshot_without_text_needs_manual_review():
    screenshot = ScreenshotArtifact(
        video_uuid=uuid4(),
        timestamp_seconds=4.0,
        vault_path="vault/raw/screenshots/source-clue.png",
        source_clue=True,
        source_clue_text=None,
    )

    triage = triage_research_basis(None, [screenshot])

    assert triage.status is ResearchBasisStatus.needs_manual_review


def test_empty_artifacts_return_no_research_source_found():
    triage = triage_research_basis(None, [])

    assert triage.status is ResearchBasisStatus.no_research_source_found
