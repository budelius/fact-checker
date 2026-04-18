from fastapi import APIRouter

from app.api import knowledge_browse, knowledge_graph, knowledge_ratings, knowledge_search

router = APIRouter(prefix="/knowledge")
router.include_router(knowledge_browse.router)
router.include_router(knowledge_search.router)
router.include_router(knowledge_graph.router)
router.include_router(knowledge_ratings.router)
