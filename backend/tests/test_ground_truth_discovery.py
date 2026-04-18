from uuid import UUID, uuid4

from app.ground_truth.dedupe import candidate_merge_keys, merge_candidates
from app.ground_truth.discovery import GroundTruthDiscoveryService
from app.ground_truth.selection import select_ground_truth_for_claim
from app.schemas.claims import ExtractedClaim
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    DiscoveryPath,
    ExternalPaperId,
    PaperAuthor,
    PaperCandidate,
    SourceProvider,
)
from app.schemas.ingestion import (
    ResearchBasisCandidate,
    ResearchBasisStatus,
    ResearchBasisTriage,
    SourceKind,
)

VIDEO_UUID = UUID("00000000-0000-4000-8000-000000000100")
TRANSCRIPT_UUID = UUID("00000000-0000-4000-8000-000000000200")


def make_claim(text: str = "Transformers use attention.") -> ExtractedClaim:
    return ExtractedClaim(
        source_video_uuid=VIDEO_UUID,
        source_transcript_uuid=TRANSCRIPT_UUID,
        claim_text=text,
        transcript_excerpt=text,
    )


def make_candidate(**overrides: object) -> PaperCandidate:
    values = {
        "title": "Attention Is All You Need",
        "kind": CandidateKind.preprint,
        "external_ids": [ExternalPaperId(provider="arxiv", value="1706.03762v7")],
        "authors": [PaperAuthor(name="Ashish Vaswani")],
        "source_url": "https://arxiv.org/abs/1706.03762",
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
        "confidence": 0.9,
        "discovery_paths": [
            DiscoveryPath(
                provider=SourceProvider.arxiv,
                query="arxiv:1706.03762",
                result_rank=1,
                url="https://arxiv.org/abs/1706.03762",
            )
        ],
    }
    values.update(overrides)
    return PaperCandidate(**values)


def test_merge_candidates_by_doi():
    first = make_candidate(external_ids=[ExternalPaperId(provider="doi", value="10.48550/ARXIV.1706.03762")])
    second = make_candidate(
        title="Attention is all you need",
        external_ids=[ExternalPaperId(provider="doi", value="10.48550/arxiv.1706.03762")],
        confidence=0.6,
    )

    merged = merge_candidates([first, second])

    assert len(merged) == 1
    assert "doi:10.48550/arxiv.1706.03762" in candidate_merge_keys(merged[0])
    assert len(merged[0].discovery_paths) == 2


def test_merge_candidates_by_arxiv_without_version():
    first = make_candidate(external_ids=[ExternalPaperId(provider="arxiv", value="1706.03762v7")])
    second = make_candidate(external_ids=[ExternalPaperId(provider="arxiv", value="1706.03762")])

    merged = merge_candidates([first, second])

    assert len(merged) == 1
    assert "arxiv:1706.03762" in candidate_merge_keys(merged[0])


def test_merge_candidates_by_title_author_fallback():
    first = make_candidate(external_ids=[], source_url=None, landing_page_url=None, pdf_url=None)
    second = make_candidate(
        title="Attention is all you need!",
        external_ids=[],
        source_url=None,
        landing_page_url=None,
        pdf_url=None,
        authors=[PaperAuthor(name="Ashish   Vaswani")],
    )

    merged = merge_candidates([first, second])

    assert len(merged) == 1
    assert candidate_merge_keys(first)[0].startswith("title_authors:")


def test_non_paper_source_is_supplemental():
    claim_uuid = uuid4()
    decisions = select_ground_truth_for_claim(
        claim_uuid,
        [make_candidate(kind=CandidateKind.non_paper, external_ids=[], source_url="https://example.com")],
    )

    assert decisions[0].status == CandidateStatus.supplemental
    assert decisions[0].reason == "non_paper_source_not_v1_ground_truth"
    assert decisions[-1].status == CandidateStatus.no_paper_found


def test_no_paper_found_decision_uses_required_reason():
    decisions = select_ground_truth_for_claim(
        uuid4(),
        [make_candidate(kind=CandidateKind.paper, confidence=0.1)],
    )

    assert decisions[-1].status == CandidateStatus.no_paper_found
    assert decisions[-1].reason == "no_scientific_evidence_found_for_now"


def test_selected_ground_truth_requires_paper_or_preprint():
    decisions = select_ground_truth_for_claim(uuid4(), [make_candidate(kind=CandidateKind.preprint)])

    assert decisions[0].status == CandidateStatus.selected_ground_truth
    assert decisions[0].reason == "paper_or_preprint_selected"


class FakeProvider:
    def __init__(self, candidates: list[PaperCandidate]) -> None:
        self.candidates = candidates
        self.queries: list[str] = []

    def search(self, query):
        self.queries.append(query.query)
        return list(self.candidates)


def make_ingestion_payload(claim: ExtractedClaim, research_basis: ResearchBasisTriage) -> dict:
    return {
        "job_uuid": str(uuid4()),
        "source_kind": SourceKind.fixture_transcript.value,
        "source_url": "fixture://attention",
        "claims": [claim.model_dump(mode="json")],
        "research_basis": research_basis.model_dump(mode="json"),
        "screenshots": [],
    }


def test_discovery_service_selects_paper_candidates():
    claim = make_claim()
    research_basis = ResearchBasisTriage(
        status=ResearchBasisStatus.source_candidates_found,
        candidates=[ResearchBasisCandidate(candidate_type="arxiv", value="1706.03762", source="test")],
        reason="fixture",
    )
    trace_events: list[dict] = []
    service = GroundTruthDiscoveryService(
        openai_web_client=FakeProvider([]),
        paper_index_clients=[FakeProvider([make_candidate()])],
        trace_sink=trace_events.append,
    )

    job = service.run_for_ingestion_payload(make_ingestion_payload(claim, research_basis))

    assert len(job.candidates) == 1
    assert any(decision.status == CandidateStatus.selected_ground_truth for decision in job.decisions)
    assert job.current_operation == "Paper candidates selected for processing."
    assert [event["stage"] for event in trace_events] == [
        "load_claims",
        "generate_queries",
        "search_openai_web",
        "search_paper_indexes",
        "merge_candidates",
        "select_sources",
    ]


def test_discovery_service_records_no_scientific_evidence():
    claim = make_claim("This is an opinion about AI research.")
    research_basis = ResearchBasisTriage(
        status=ResearchBasisStatus.opinion_or_unratable,
        candidates=[],
        reason="No references.",
    )
    service = GroundTruthDiscoveryService(
        openai_web_client=FakeProvider([]),
        paper_index_clients=[FakeProvider([])],
    )

    job = service.run_for_ingestion_payload(make_ingestion_payload(claim, research_basis))

    assert job.candidates == []
    assert job.current_operation == "No scientific evidence found for now."
    assert job.decisions[-1].status == CandidateStatus.no_paper_found
    assert job.decisions[-1].reason == "no_scientific_evidence_found_for_now"
