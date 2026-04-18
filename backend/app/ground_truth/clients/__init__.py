"""Provider clients for Phase 3 source discovery."""

from app.ground_truth.clients.arxiv import ArxivClient
from app.ground_truth.clients.openai_search import OpenAIWebSearchClient
from app.ground_truth.clients.openalex import OpenAlexClient
from app.ground_truth.clients.semantic_scholar import SemanticScholarClient

__all__ = [
    "ArxivClient",
    "OpenAIWebSearchClient",
    "OpenAlexClient",
    "SemanticScholarClient",
]
