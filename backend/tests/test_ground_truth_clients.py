from uuid import UUID

from app.ground_truth.queries import build_discovery_queries
from app.schemas.claims import ExtractedClaim
from app.schemas.ingestion import (
    ResearchBasisCandidate,
    ResearchBasisStatus,
    ResearchBasisTriage,
    ScreenshotArtifact,
)


VIDEO_UUID = UUID("00000000-0000-4000-8000-000000000100")
TRANSCRIPT_UUID = UUID("00000000-0000-4000-8000-000000000200")


def _claim(claim_text: str, transcript_excerpt: str) -> ExtractedClaim:
    return ExtractedClaim(
        source_video_uuid=VIDEO_UUID,
        source_transcript_uuid=TRANSCRIPT_UUID,
        claim_text=claim_text,
        transcript_excerpt=transcript_excerpt,
    )


def test_build_discovery_queries_prefers_identifiers():
    doi_candidate = ResearchBasisCandidate(
        candidate_type="doi",
        value="10.48550/arXiv.1706.03762",
        source="transcript",
    )
    arxiv_candidate = ResearchBasisCandidate(
        candidate_type="arxiv",
        value="1706.03762",
        source="transcript",
    )
    title_candidate = ResearchBasisCandidate(
        candidate_type="paper_title",
        value="Attention Is All You Need",
        source="transcript",
    )
    research_basis = ResearchBasisTriage(
        status=ResearchBasisStatus.source_candidates_found,
        candidates=[title_candidate, arxiv_candidate, doi_candidate],
        reason="fixture",
    )

    queries = build_discovery_queries([_claim("Transformers use self attention.", "the paper")], research_basis)

    assert [query.query for query in queries[:3]] == [
        "10.48550/arXiv.1706.03762",
        "arxiv:1706.03762",
        '"Attention Is All You Need"',
    ]
    assert queries[0].provider_hint == "doi"
    assert queries[1].provider_hint == "arxiv"
    assert queries[0].source_candidate_uuid == doi_candidate.uuid
    assert queries[0].reason == ["exact doi identifier from Phase 2 source candidate"]


def test_build_discovery_queries_adds_claim_and_screenshot_queries():
    claim = _claim(
        "The transformer architecture relies only on attention mechanisms.",
        "They said the transformer relies only on attention mechanisms.",
    )
    screenshot = ScreenshotArtifact(
        video_uuid=VIDEO_UUID,
        vault_path="vault/raw/screenshots/source.png",
        source_clue=True,
        source_clue_text="Attention Is All You Need arxiv screenshot",
    )

    queries = build_discovery_queries([claim], [], screenshots=[screenshot])

    assert [query.query for query in queries] == [
        "The transformer architecture relies only on attention mechanisms.",
        "They said the transformer relies only on attention mechanisms.",
        "Attention Is All You Need arxiv screenshot",
    ]
    assert queries[0].claim_uuid == claim.uuid
    assert queries[0].reason == ["semantic claim query from ExtractedClaim.claim_text"]
    assert queries[2].provider_hint == "source_clue_text"
    assert queries[2].reason == ["screenshot source_clue_text query"]
