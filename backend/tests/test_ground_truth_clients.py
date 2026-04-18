import json
from pathlib import Path
from uuid import UUID

from app.ground_truth.clients.arxiv import ArxivClient, parse_arxiv_atom
from app.ground_truth.clients.openai_search import (
    OpenAIWebSearchClient,
    parse_openai_web_search_response,
)
from app.ground_truth.clients.openalex import OpenAlexClient, parse_openalex_works
from app.ground_truth.clients.semantic_scholar import (
    SemanticScholarClient,
    parse_semantic_scholar_papers,
)
from app.ground_truth.queries import build_discovery_queries
from app.schemas.claims import ExtractedClaim
from app.schemas.ground_truth import CandidateKind, CandidateStatus, SourceProvider
from app.schemas.ingestion import (
    ResearchBasisCandidate,
    ResearchBasisStatus,
    ResearchBasisTriage,
    ScreenshotArtifact,
)


VIDEO_UUID = UUID("00000000-0000-4000-8000-000000000100")
TRANSCRIPT_UUID = UUID("00000000-0000-4000-8000-000000000200")
FIXTURE_DIR = Path("tests/fixtures/ground_truth")


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


def test_arxiv_client_parses_atom_fixture():
    query = build_discovery_queries([], [ResearchBasisCandidate(candidate_type="arxiv", value="1706.03762", source="fixture")])[0]

    candidates = parse_arxiv_atom((FIXTURE_DIR / "arxiv_attention.xml").read_text(), query)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.title == "Attention Is All You Need"
    assert candidate.kind == CandidateKind.preprint
    assert candidate.pdf_url == "http://arxiv.org/pdf/1706.03762v7"
    assert candidate.external_ids[0].provider == "arxiv"
    assert candidate.discovery_paths[0].provider == SourceProvider.arxiv


def test_openalex_client_parses_work_fixture():
    query = build_discovery_queries([_claim("Transformers use attention.", "attention")], [])[0]
    payload = json.loads((FIXTURE_DIR / "openalex_attention.json").read_text())

    candidates = parse_openalex_works(payload, query)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.title == "Attention Is All You Need"
    assert candidate.kind == CandidateKind.preprint
    assert candidate.pdf_url == "https://arxiv.org/pdf/1706.03762.pdf"
    assert candidate.abstract == "We propose the Transformer"
    assert candidate.discovery_paths[0].provider == SourceProvider.openalex


def test_semantic_scholar_client_parses_paper_fixture():
    query = build_discovery_queries([_claim("Transformers use attention.", "attention")], [])[0]
    payload = json.loads((FIXTURE_DIR / "semantic_scholar_attention.json").read_text())

    candidates = parse_semantic_scholar_papers(payload, query)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.title == "Attention Is All You Need"
    assert candidate.kind == CandidateKind.paper
    assert candidate.pdf_url == "https://arxiv.org/pdf/1706.03762.pdf"
    assert candidate.external_ids[0].provider == "semantic_scholar"
    assert candidate.discovery_paths[0].provider == SourceProvider.semantic_scholar


def test_provider_clients_expose_search_methods():
    assert hasattr(ArxivClient, "search")
    assert hasattr(OpenAlexClient, "search")
    assert hasattr(SemanticScholarClient, "search")
    assert hasattr(OpenAIWebSearchClient, "search")


def test_openai_web_search_preserves_citations_and_sources():
    query = build_discovery_queries([_claim("Transformers use attention.", "attention")], [])[0]
    payload = json.loads((FIXTURE_DIR / "openai_web_search_attention.json").read_text())

    candidates = parse_openai_web_search_response(payload, query)

    assert [candidate.source_url for candidate in candidates] == [
        "https://arxiv.org/abs/1706.03762",
        "https://example.com/attention-blog",
    ]
    assert candidates[0].title == "Attention Is All You Need"
    assert candidates[0].kind == CandidateKind.preprint
    assert candidates[0].status == CandidateStatus.needs_manual_review
    assert candidates[1].kind == CandidateKind.non_paper
    assert candidates[1].status == CandidateStatus.supplemental
    assert candidates[0].discovery_paths[0].provider == SourceProvider.openai_web


def test_openai_web_search_does_not_leak_api_key():
    query = build_discovery_queries([_claim("Transformers use attention.", "attention")], [])[0]
    payload = json.loads((FIXTURE_DIR / "openai_web_search_attention.json").read_text())
    payload["output"][0]["content"][0]["annotations"][0]["api_key"] = "sk-test-secret"

    candidates = parse_openai_web_search_response(payload, query)

    serialized = json.dumps([candidate.raw_provider_data for candidate in candidates])
    assert "sk-test-secret" not in serialized
    assert "[redacted]" in serialized
