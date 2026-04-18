import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ground_truth import router as ground_truth_router
from app.api.ingestion import router as ingestion_router
from app.api.knowledge import router as knowledge_router
from app.api.reports import router as reports_router

app = FastAPI(title="Fact Checker API")

_default_cors_origins = "http://127.0.0.1:5173,http://localhost:5173"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOW_ORIGINS", _default_cors_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router)
app.include_router(ground_truth_router)
app.include_router(reports_router)
app.include_router(knowledge_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fact-checker-backend"}


@app.get("/contracts")
def contracts() -> dict[str, str]:
    return {
        "identity": "uuid",
        "metadata_store": "mongodb",
        "vector_store": "qdrant",
        "vault": "markdown",
    }
