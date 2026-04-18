from uuid import UUID

from app.ground_truth.indexing import index_paper_chunks, index_paper_summaries
from app.schemas.entities import EntityType
from app.schemas.ground_truth import PaperChunk, PaperMetadata, PaperSummary

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
SOURCE_UUID = UUID("00000000-0000-4000-8000-000000000003")
RELATIONSHIP_UUID = UUID("00000000-0000-4000-8000-000000000004")


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.texts: list[str] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.texts.extend(texts)
        return [[float(index), 0.25, 0.5] for index, _ in enumerate(texts, start=1)]


class FakeQdrantRepository:
    def __init__(self) -> None:
        self.vector_size: int | None = None
        self.points = []

    def ensure_collection(self, vector_size: int) -> None:
        self.vector_size = vector_size

    def upsert_payload(self, payload, vector: list[float]) -> None:
        self.points.append((payload, vector))


def make_chunk() -> PaperChunk:
    return PaperChunk(
        paper_uuid=PAPER_UUID,
        source_uuid=SOURCE_UUID,
        chunk_id="paper-0001-0001",
        text="Scaled dot-product attention.",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
        source_url="https://arxiv.org/abs/1706.03762",
    )


def test_index_paper_chunks_uses_trace_payloads():
    qdrant = FakeQdrantRepository()
    embeddings = FakeEmbeddingProvider()

    count = index_paper_chunks(qdrant, embeddings, [make_chunk()], [RELATIONSHIP_UUID])

    assert count == 1
    assert qdrant.vector_size == 3
    payload, vector = qdrant.points[0]
    assert vector == [1.0, 0.25, 0.5]
    assert payload.uuid == PAPER_UUID
    assert payload.entity_type == EntityType.evidence
    assert payload.chunk_id == "paper-0001-0001"
    assert payload.source == "paper"
    assert payload.source_uuid == SOURCE_UUID
    assert payload.relationship_uuids == [RELATIONSHIP_UUID]
    assert payload.vault_path == "vault/wiki/papers/attention-is-all-you-need.md"


def test_index_paper_summaries_uses_paper_payloads():
    qdrant = FakeQdrantRepository()
    embeddings = FakeEmbeddingProvider()
    metadata = PaperMetadata(
        uuid=PAPER_UUID,
        title="Attention Is All You Need",
        publication_status="preprint",
        vault_path="vault/wiki/papers/attention-is-all-you-need.md",
    )
    summary = PaperSummary(paper_uuid=PAPER_UUID, summary_markdown="Transformer summary.")

    count = index_paper_summaries(
        qdrant,
        embeddings,
        [summary],
        {PAPER_UUID: metadata},
        {PAPER_UUID: [RELATIONSHIP_UUID]},
    )

    assert count == 1
    assert qdrant.vector_size == 3
    payload, _ = qdrant.points[0]
    assert payload.uuid == PAPER_UUID
    assert payload.entity_type == EntityType.paper
    assert payload.chunk_id == "summary"
    assert payload.source == "paper_summary"
    assert payload.relationship_uuids == [RELATIONSHIP_UUID]
    assert payload.vault_path == "vault/wiki/papers/attention-is-all-you-need.md"
