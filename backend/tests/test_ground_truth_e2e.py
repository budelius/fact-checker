from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.ground_truth import (
    clear_ground_truth_jobs_for_tests,
    get_pipeline,
    get_qdrant_repository,
    get_repository,
    get_vault_root,
)
from app.ground_truth.discovery import GroundTruthDiscoveryService
from app.ground_truth.pipeline import GroundTruthPipeline
from app.ingestion.jobs import clear_jobs_for_tests
from app.main import app
from app.schemas.ground_truth import (
    CandidateKind,
    CandidateStatus,
    DiscoveryPath,
    ExternalPaperId,
    PaperCandidate,
    SourceProvider,
)
from app.settings import Settings, get_settings

client = TestClient(app)


def setup_function(_function):
    clear_jobs_for_tests()
    clear_ground_truth_jobs_for_tests()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def make_settings(monkeypatch, tmp_path) -> Settings:
    monkeypatch.setenv("MONGODB_URI", "mongodb://example")
    monkeypatch.setenv("MONGODB_DATABASE", "fact_checker")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_COLLECTION_KNOWLEDGE", "fact_checker_knowledge")
    monkeypatch.setenv("VAULT_ROOT", str(tmp_path / "vault"))
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    get_settings.cache_clear()
    return Settings()


class FakeProvider:
    def __init__(self, candidates: list[PaperCandidate]) -> None:
        self.candidates = candidates

    def search(self, _query):
        return list(self.candidates)


class FakeResponse:
    status_code = 200
    url = "https://arxiv.org/pdf/1706.03762.pdf"
    headers = {"content-type": "application/pdf"}

    def __init__(self) -> None:
        self.content = open("tests/fixtures/ground_truth/sample-paper.pdf", "rb").read()


class FakeHttpClient:
    def get(self, *_args, **_kwargs):
        return FakeResponse()


class FakeRepository:
    def __init__(self) -> None:
        self.entities = []
        self.relationships = []

    def upsert_entity(self, entity) -> None:
        self.entities.append(entity)

    def upsert_relationship(self, relationship) -> None:
        self.relationships.append(relationship)


class FakeQdrantRepository:
    def __init__(self) -> None:
        self.vector_size = None
        self.points = []

    def ensure_collection(self, vector_size: int) -> None:
        self.vector_size = vector_size

    def upsert_payload(self, payload, vector) -> None:
        self.points.append((payload, vector))


class FakeEmbeddingProvider:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 0.5, 0.25] for index, _ in enumerate(texts, start=1)]


def paper_candidate() -> PaperCandidate:
    return PaperCandidate(
        title="Attention Is All You Need",
        kind=CandidateKind.preprint,
        status=CandidateStatus.needs_manual_review,
        external_ids=[ExternalPaperId(provider="arxiv", value="1706.03762")],
        source_url="https://arxiv.org/abs/1706.03762",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        confidence=0.95,
        discovery_paths=[
            DiscoveryPath(
                provider=SourceProvider.arxiv,
                query="arxiv:1706.03762",
                result_rank=1,
                url="https://arxiv.org/abs/1706.03762",
            )
        ],
    )


def supplemental_candidate() -> PaperCandidate:
    return PaperCandidate(
        title="Attention blog",
        kind=CandidateKind.non_paper,
        status=CandidateStatus.supplemental,
        source_url="https://example.com/attention-blog",
        confidence=0.3,
        discovery_paths=[
            DiscoveryPath(
                provider=SourceProvider.openai_web,
                query="attention blog",
                result_rank=2,
                url="https://example.com/attention-blog",
            )
        ],
    )


def ingestion_payload() -> dict:
    claim_uuid = uuid4()
    return {
        "job_uuid": str(uuid4()),
        "source_url": "fixture://attention",
        "claims": [
            {
                "uuid": str(claim_uuid),
                "source_video_uuid": str(uuid4()),
                "source_transcript_uuid": str(uuid4()),
                "transcript_excerpt": "The source is arXiv:1706.03762.",
                "claim_text": "Transformers rely on attention.",
                "screenshot_uuids": [],
                "evidence_status": "pending",
                "source_candidate_count": 1,
            }
        ],
        "research_basis": {
            "status": "source_candidates_found",
            "reason": "fixture",
            "candidates": [
                {
                    "candidate_type": "arxiv",
                    "value": "1706.03762",
                    "source": "transcript",
                }
            ],
        },
        "screenshots": [],
    }


def build_pipeline(settings: Settings, candidates: list[PaperCandidate]) -> GroundTruthPipeline:
    return GroundTruthPipeline(
        discovery_service=GroundTruthDiscoveryService(
            openai_web_client=FakeProvider([candidate for candidate in candidates if candidate.kind == CandidateKind.non_paper]),
            paper_index_clients=[FakeProvider([candidate for candidate in candidates if candidate.kind != CandidateKind.non_paper])],
        ),
        settings=settings,
        acquisition_client=FakeHttpClient(),
        embedding_provider=FakeEmbeddingProvider(),
    )


def test_ground_truth_pipeline_processes_selected_paper_fixture(monkeypatch, tmp_path):
    settings = make_settings(monkeypatch, tmp_path)
    repository = FakeRepository()
    qdrant = FakeQdrantRepository()
    pipeline = build_pipeline(settings, [paper_candidate(), supplemental_candidate()])

    job = pipeline.run_from_ingestion_payload(
        ingestion_payload(),
        repository=repository,
        qdrant_repository=qdrant,
        vault_root=tmp_path / "vault",
    )

    assert {decision.status for decision in job.decisions} >= {
        CandidateStatus.selected_ground_truth,
        CandidateStatus.supplemental,
    }
    assert len(job.papers) == 1
    assert job.papers[0].vault_path == "vault/wiki/papers/attention-is-all-you-need.md"
    assert len(job.chunks) >= 1
    assert (tmp_path / "vault" / "wiki" / "papers" / "attention-is-all-you-need.md").exists()
    assert qdrant.points


def test_ground_truth_pipeline_handles_no_paper_found(monkeypatch, tmp_path):
    settings = make_settings(monkeypatch, tmp_path)
    pipeline = build_pipeline(settings, [])

    job = pipeline.run_from_ingestion_payload(
        ingestion_payload(),
        repository=FakeRepository(),
        qdrant_repository=FakeQdrantRepository(),
        vault_root=tmp_path / "vault",
    )

    assert job.current_operation == "No scientific evidence found for now."
    assert job.chunks == []
    assert job.decisions[-1].status == CandidateStatus.no_paper_found


def test_ground_truth_api_fixture_path_processes_selected_paper(monkeypatch, tmp_path):
    settings = make_settings(monkeypatch, tmp_path)
    repository = FakeRepository()
    qdrant = FakeQdrantRepository()
    pipeline = build_pipeline(settings, [paper_candidate(), supplemental_candidate()])
    app.dependency_overrides[get_pipeline] = lambda: pipeline
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_qdrant_repository] = lambda: qdrant
    app.dependency_overrides[get_vault_root] = lambda: tmp_path / "vault"

    ingestion_response = client.post(
        "/ingestion/fixtures/transcript",
        json={
            "source_url": "https://www.tiktok.com/@fixture/video/1234567890",
            "title": "Attention paper explained",
            "transcript": (
                "00:00:01.000 --> 00:00:03.500\n"
                "A paper says transformers scale well for sequence modeling.\n\n"
                "00:00:04.000 --> 00:00:05.500\n"
                "The source is arXiv:1706.03762."
            ),
        },
    )
    ingestion_payload_response = ingestion_response.json()

    response = client.post(
        f"/ground-truth/jobs/from-ingestion/{ingestion_payload_response['job_uuid']}"
    )

    assert response.status_code == 200
    payload = response.json()
    serialized = str(payload)
    assert "supported" not in serialized
    assert "contradicted" not in serialized
    assert "mixed" not in serialized
    assert "insufficient" not in serialized
    assert {decision["status"] for decision in payload["decisions"]} >= {
        "selected_ground_truth",
        "supplemental",
    }
    assert payload["papers"][0]["vault_path"] == "vault/wiki/papers/attention-is-all-you-need.md"
    assert payload["chunks"]
    assert qdrant.points

    fetched_ingestion = client.get(f"/ingestion/jobs/{ingestion_payload_response['job_uuid']}")
    assert fetched_ingestion.json()["claims"][0]["evidence_status"] == "pending"

    fetched_ground_truth = client.get(f"/ground-truth/jobs/{payload['job_uuid']}")
    assert fetched_ground_truth.status_code == 200
    assert fetched_ground_truth.json()["job_uuid"] == payload["job_uuid"]
