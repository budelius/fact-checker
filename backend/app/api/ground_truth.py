from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo import MongoClient

from app.ground_truth.clients import (
    ArxivClient,
    OpenAIWebSearchClient,
    OpenAlexClient,
    SemanticScholarClient,
)
from app.ground_truth.discovery import GroundTruthDiscoveryService
from app.ground_truth.indexing import OpenAIEmbeddingProvider
from app.ground_truth.pipeline import GroundTruthPipeline
from app.ground_truth.summarization import PaperSummarizer
from app.ingestion.jobs import get_job
from app.repositories.mongo import MongoRepository
from app.repositories.qdrant import QdrantRepository
from app.schemas.ground_truth import GroundTruthJob
from app.settings import Settings, get_settings

router = APIRouter(prefix="/ground-truth", tags=["ground-truth"])

_GROUND_TRUTH_JOB_STORE: dict[str, dict] = {}


def clear_ground_truth_jobs_for_tests() -> None:
    _GROUND_TRUTH_JOB_STORE.clear()


def serialize_ground_truth_job(job: GroundTruthJob) -> dict:
    payload = jsonable_encoder(job)
    _GROUND_TRUTH_JOB_STORE[str(job.job_uuid)] = payload
    return payload


def get_ground_truth_job(job_uuid: UUID) -> dict | None:
    return _GROUND_TRUTH_JOB_STORE.get(str(job_uuid))


def get_pipeline(settings: Settings = Depends(get_settings)) -> GroundTruthPipeline:
    paper_clients = [
        ArxivClient(max_results=settings.ground_truth_max_results_per_provider),
        OpenAlexClient(
            max_results=settings.ground_truth_max_results_per_provider,
            mailto=settings.openalex_email,
        ),
        SemanticScholarClient(
            max_results=settings.ground_truth_max_results_per_provider,
            api_key=settings.semantic_scholar_api_key,
        ),
    ]
    openai_client = OpenAIWebSearchClient(settings) if settings.openai_api_key else None
    return GroundTruthPipeline(
        discovery_service=GroundTruthDiscoveryService(
            openai_web_client=openai_client,
            paper_index_clients=paper_clients,
        ),
        settings=settings,
        summarizer=PaperSummarizer(settings) if settings.openai_api_key else None,
        embedding_provider=OpenAIEmbeddingProvider(settings) if settings.openai_api_key else None,
    )


def get_repository(settings: Settings = Depends(get_settings)) -> MongoRepository:
    return MongoRepository(MongoClient(settings.mongodb_uri), settings.mongodb_database)


def get_qdrant_repository(settings: Settings = Depends(get_settings)) -> QdrantRepository:
    return QdrantRepository(settings.qdrant_url, settings.qdrant_collection_knowledge)


def get_vault_root(settings: Settings = Depends(get_settings)) -> Path:
    return Path(settings.vault_root)


@router.post("/jobs/from-ingestion/{ingestion_job_uuid}")
def start_ground_truth_job_from_ingestion(
    ingestion_job_uuid: UUID,
    pipeline: GroundTruthPipeline = Depends(get_pipeline),
    repository=Depends(get_repository),
    qdrant_repository=Depends(get_qdrant_repository),
    vault_root: Path = Depends(get_vault_root),
) -> dict:
    ingestion_payload = get_job(ingestion_job_uuid)
    if ingestion_payload is None:
        raise HTTPException(status_code=404, detail="ingestion_job_not_found")
    if not ingestion_payload.get("claims"):
        raise HTTPException(status_code=400, detail="ingestion_job_has_no_claims")

    job = pipeline.run_from_ingestion_payload(
        ingestion_payload,
        repository=repository,
        qdrant_repository=qdrant_repository,
        vault_root=vault_root,
    )
    return serialize_ground_truth_job(job)


@router.get("/jobs/{job_uuid}")
def fetch_ground_truth_job(job_uuid: UUID) -> dict:
    job = get_ground_truth_job(job_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="ground_truth_job_not_found")
    return job
