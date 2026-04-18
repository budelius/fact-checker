"""Knowledge search routes backed by Qdrant when embeddings are configured."""

from pathlib import Path

from fastapi import APIRouter, Depends, Query

from app.api.ground_truth import get_qdrant_repository, get_vault_root
from app.ground_truth.indexing import OpenAIEmbeddingProvider
from app.knowledge.search import search_knowledge
from app.schemas.entities import EntityType
from app.settings import Settings, get_settings

router = APIRouter(tags=["knowledge-search"])


@router.get("/search")
def search(
    q: str = "",
    entity_type: list[EntityType] | None = Query(default=None),
    limit: int = 10,
    settings: Settings = Depends(get_settings),
    qdrant_repository=Depends(get_qdrant_repository),
    vault_root: Path = Depends(get_vault_root),
) -> dict:
    embedding_provider = OpenAIEmbeddingProvider(settings) if settings.openai_api_key else None
    entity_types = [item.value for item in entity_type] if entity_type else None
    results = search_knowledge(
        q,
        qdrant_repository=qdrant_repository,
        embedding_provider=embedding_provider,
        vault_root=vault_root,
        entity_types=entity_types,
        limit=limit,
    )
    return {
        "query": q,
        "results": results,
        "count": len(results),
        "vector_backed": any(result.vector_backed for result in results),
    }
