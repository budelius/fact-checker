import re

from app.schemas.ingestion import (
    ResearchBasisCandidate,
    ResearchBasisStatus,
    ResearchBasisTriage,
    ScreenshotArtifact,
    TranscriptArtifact,
)

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ARXIV_PATTERN = re.compile(r"\b(?:arXiv:\s*)?(\d{4}\.\d{4,5})(?:v\d+)?\b", re.IGNORECASE)
ARXIV_URL_PATTERN = re.compile(r"arxiv\.org/abs/(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s)>\]]+", re.IGNORECASE)
PAPER_REFERENCE_PATTERN = re.compile(
    r"\b(?:paper|study|preprint|researchers|arxiv)\b",
    re.IGNORECASE,
)


def _candidate(candidate_type: str, value: str, source: str, source_uuid) -> ResearchBasisCandidate:
    return ResearchBasisCandidate(
        candidate_type=candidate_type,
        value=value.rstrip(".,;"),
        source=source,
        source_uuid=source_uuid,
    )


def _extract_from_text(text: str, source: str, source_uuid) -> list[ResearchBasisCandidate]:
    candidates: list[ResearchBasisCandidate] = []

    candidates.extend(
        _candidate("doi", match.group(0), source, source_uuid) for match in DOI_PATTERN.finditer(text)
    )
    candidates.extend(
        _candidate("arxiv", match.group(1), source, source_uuid)
        for match in ARXIV_URL_PATTERN.finditer(text)
    )
    candidates.extend(
        _candidate("arxiv", match.group(1), source, source_uuid)
        for match in ARXIV_PATTERN.finditer(text)
    )
    candidates.extend(
        _candidate("url", match.group(0), source, source_uuid) for match in URL_PATTERN.finditer(text)
    )

    if PAPER_REFERENCE_PATTERN.search(text):
        candidates.append(_candidate("paper_title", text.strip()[:240], source, source_uuid))

    return candidates


def extract_research_basis_candidates(
    transcript: TranscriptArtifact,
    screenshots: list[ScreenshotArtifact],
) -> list[ResearchBasisCandidate]:
    candidates = _extract_from_text(
        transcript.plain_text,
        source="transcript",
        source_uuid=transcript.transcript_uuid,
    )

    for screenshot in screenshots:
        if screenshot.source_clue_text:
            candidates.extend(
                _extract_from_text(
                    screenshot.source_clue_text,
                    source="screenshot",
                    source_uuid=screenshot.screenshot_uuid,
                )
            )

    return candidates


def triage_research_basis(
    transcript: TranscriptArtifact | None,
    screenshots: list[ScreenshotArtifact],
) -> ResearchBasisTriage:
    if transcript is not None:
        candidates = extract_research_basis_candidates(transcript, screenshots)
        if candidates:
            return ResearchBasisTriage(
                status=ResearchBasisStatus.source_candidates_found,
                candidates=candidates,
                reason="Source candidates found in transcript or screenshot context.",
            )

    if any(screenshot.source_clue and not screenshot.source_clue_text for screenshot in screenshots):
        return ResearchBasisTriage(
            status=ResearchBasisStatus.needs_manual_review,
            candidates=[],
            reason="Source-clue screenshots exist but no readable clue text is available.",
        )

    if transcript is not None:
        return ResearchBasisTriage(
            status=ResearchBasisStatus.opinion_or_unratable,
            candidates=[],
            reason="No paper or source references found in transcript or screenshots.",
        )

    return ResearchBasisTriage(
        status=ResearchBasisStatus.no_research_source_found,
        candidates=[],
        reason="No transcript or readable source-clue artifacts are available.",
    )
