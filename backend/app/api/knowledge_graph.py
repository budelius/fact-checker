"""Graph and consistency routes for the owned knowledge store."""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.ground_truth import get_qdrant_repository, get_repository, get_vault_root
from app.knowledge.consistency import check_knowledge_consistency
from app.knowledge.graph import build_entity_graph
from app.schemas.knowledge import KnowledgeConsistencySummary, KnowledgeGraphResponse

router = APIRouter(tags=["knowledge-graph"])


@router.get("/graph/{entity_uuid}", response_model=KnowledgeGraphResponse)
def fetch_graph(
    entity_uuid: UUID,
    depth: int = 1,
    repository=Depends(get_repository),
) -> KnowledgeGraphResponse:
    return build_entity_graph(entity_uuid, repository=repository, depth=depth)


@router.get("/consistency", response_model=KnowledgeConsistencySummary)
def fetch_consistency(
    repository=Depends(get_repository),
    qdrant_repository=Depends(get_qdrant_repository),
    vault_root: Path = Depends(get_vault_root),
) -> KnowledgeConsistencySummary:
    return check_knowledge_consistency(vault_root, repository, qdrant_repository)
