from typing import Protocol
from uuid import UUID

from openai import OpenAI

from app.schemas.entities import EntityType
from app.schemas.ground_truth import PaperChunk, PaperMetadata, PaperSummary
from app.schemas.vector_payloads import QdrantPayload
from app.settings import Settings


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Settings, client: OpenAI | None = None) -> None:
        self.settings = settings
        self.client = client or OpenAI(api_key=settings.openai_api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        kwargs = {
            "model": self.settings.openai_embedding_model,
            "input": texts,
        }
        if self.settings.openai_embedding_dimensions is not None:
            kwargs["dimensions"] = self.settings.openai_embedding_dimensions
        response = self.client.embeddings.create(**kwargs)
        return [item.embedding for item in response.data]


def _ensure_and_upsert(qdrant_repository, payloads: list[QdrantPayload], vectors: list[list[float]]) -> int:
    if not payloads:
        return 0
    qdrant_repository.ensure_collection(vector_size=len(vectors[0]))
    for payload, vector in zip(payloads, vectors, strict=True):
        qdrant_repository.upsert_payload(payload, vector)
    return len(payloads)


def index_paper_chunks(
    qdrant_repository,
    embedding_provider: EmbeddingProvider,
    chunks: list[PaperChunk],
    relationship_uuids: list[UUID],
) -> int:
    vectors = embedding_provider.embed_texts([chunk.text for chunk in chunks]) if chunks else []
    payloads = [
        QdrantPayload(
            uuid=chunk.paper_uuid,
            entity_type=EntityType.evidence,
            vault_path=chunk.vault_path,
            chunk_id=chunk.chunk_id,
            source="paper",
            source_uuid=chunk.source_uuid,
            relationship_uuids=relationship_uuids,
        )
        for chunk in chunks
    ]
    return _ensure_and_upsert(qdrant_repository, payloads, vectors)


def index_paper_summaries(
    qdrant_repository,
    embedding_provider: EmbeddingProvider,
    summaries: list[PaperSummary],
    metadata_by_paper_uuid: dict[UUID, PaperMetadata],
    relationship_uuids_by_paper_uuid: dict[UUID, list[UUID]],
) -> int:
    vectors = (
        embedding_provider.embed_texts([summary.summary_markdown for summary in summaries])
        if summaries
        else []
    )
    payloads = []
    for summary in summaries:
        metadata = metadata_by_paper_uuid[summary.paper_uuid]
        payloads.append(
            QdrantPayload(
                uuid=summary.paper_uuid,
                entity_type=EntityType.paper,
                vault_path=metadata.vault_path or "",
                chunk_id="summary",
                source="paper_summary",
                relationship_uuids=relationship_uuids_by_paper_uuid.get(summary.paper_uuid, []),
            )
        )
    return _ensure_and_upsert(qdrant_repository, payloads, vectors)
