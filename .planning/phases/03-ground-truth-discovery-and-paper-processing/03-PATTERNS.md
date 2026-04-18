# Phase 3: Ground-Truth Discovery and Paper Processing - Pattern Map

**Mapped:** 2026-04-18
**Status:** Ready for planning
**Source:** Local orchestrator fallback; no pattern-mapper subagent used in this run.

## Purpose

This file maps Phase 3 implementation areas to existing repo analogs and contracts. It is a planner input only; `03-CONTEXT.md` and `03-RESEARCH.md` remain authoritative for scope and technical decisions.

## Backend Patterns

### API Router

**Likely files**

- `backend/app/api/ground_truth.py`
- `backend/app/main.py`

**Closest existing analog**

- `backend/app/api/ingestion.py` defines an `APIRouter(prefix="/ingestion", tags=["ingestion"])`, request DTOs, helper functions, and route functions.
- `backend/app/main.py` includes the ingestion router with `app.include_router(ingestion_router)`.

**Planning guidance**

- Add a separate `ground_truth` router rather than extending the ingestion router.
- Keep Phase 3 routes thin: validate request, call a pipeline service, return a normalized job payload.
- Recommended routes:
  - `POST /ground-truth/jobs/from-ingestion/{job_uuid}`
  - `GET /ground-truth/jobs/{job_uuid}`

### Pydantic Schemas

**Likely files**

- `backend/app/schemas/ground_truth.py`
- `backend/app/schemas/__init__.py`

**Closest existing analog**

- `backend/app/schemas/ingestion.py` uses Pydantic models, enums, UUID defaults, and `Field(default_factory=list)`.
- `backend/app/schemas/claims.py` keeps evidence status pending during ingestion.

**Planning guidance**

- Follow the same enum/string model style.
- Use UUID defaults for Phase 3 jobs, candidates, decisions, paper records, chunks, and summaries.
- Keep source/provider IDs as external IDs and aliases, not canonical UUIDs.

### Provider Clients

**Likely files**

- `backend/app/ground_truth/clients/openai_search.py`
- `backend/app/ground_truth/clients/arxiv.py`
- `backend/app/ground_truth/clients/openalex.py`
- `backend/app/ground_truth/clients/semantic_scholar.py`

**Closest existing analog**

- `backend/app/ingestion/adapters/tiktok.py` isolates platform-specific behavior behind an adapter.
- `backend/app/ingestion/research_basis.py` normalizes source hints without leaking adapter behavior.

**Planning guidance**

- Isolate every external API behind a small client returning `PaperCandidate` records.
- Tests should use fake transports or static fixtures; no live network calls in unit tests.
- Store raw provider snippets/results in trace metadata with secrets removed.

### Pipeline Logging

**Likely files**

- `backend/app/contracts/logging.py`
- `backend/app/ground_truth/progress.py`
- `backend/app/repositories/mongo.py`

**Closest existing analog**

- `build_pipeline_log_event()` already validates event type/status and returns a structured event dict.
- `MongoRepository` exposes `pipeline_events`.

**Planning guidance**

- Extend event types if needed for `source_discovery`, `paper_processing`, and `summarization`.
- Every provider call, merge decision, selection/rejection, acquisition decision, parse result, summary write, and index write should create an event record.

### Vault Paths And Markdown

**Likely files**

- `backend/app/contracts/vault.py`
- `vault/SCHEMA.md`
- `backend/app/ground_truth/markdown.py`
- `backend/app/ground_truth/persistence.py`

**Closest existing analog**

- `expected_wiki_path(entity_type, slug)` produces slug-only Markdown note paths.
- `expected_raw_artifact_path(kind, slug, extension)` produces raw artifact paths.
- `vault/SCHEMA.md` defines raw/wiki split and frontmatter keys.

**Planning guidance**

- Extend raw artifacts with `papers`.
- Keep downloaded PDFs under `vault/raw/papers/`.
- Put generated paper notes under `vault/wiki/papers/`.
- Frontmatter should contain UUID, entity type, slug, title, aliases, external IDs, relationships, created_at, and updated_at.

### MongoDB Persistence

**Likely files**

- `backend/app/repositories/mongo.py`
- `backend/app/ground_truth/persistence.py`

**Closest existing analog**

- `MongoRepository.upsert_entity()` upserts by UUID.
- `MongoRepository.upsert_relationship()` upserts by relationship UUID.

**Planning guidance**

- Add or use collections for `ground_truth_jobs`, `source_candidates`, `source_decisions`, `paper_records`, and `paper_chunks` if job-specific records should not be mixed into canonical `entities`.
- Upsert canonical entities by UUID, but dedupe before UUID creation by DOI/arXiv/OpenAlex/Semantic Scholar/title-authors.

### Qdrant Indexing

**Likely files**

- `backend/app/repositories/qdrant.py`
- `backend/app/schemas/vector_payloads.py`
- `backend/app/ground_truth/indexing.py`

**Closest existing analog**

- `QdrantRepository.upsert_payload()` uses deterministic point IDs based on payload UUID plus chunk ID.
- `QdrantPayload` already includes `uuid`, `entity_type`, `vault_path`, `chunk_id`, `source`, `source_date`, `source_uuid`, `relationship_uuid`, and `relationship_uuids`.

**Planning guidance**

- Reuse `QdrantPayload` for paper chunks and summaries.
- Use fake vectors in tests.
- Infer vector size from configured/test embedding provider output before ensuring the collection.

### Untrusted Input Boundary

**Likely files**

- `backend/app/ground_truth/summarization.py`
- `backend/app/safety/input_boundaries.py`

**Closest existing analog**

- `wrap_untrusted_text(label, content)` wraps transcripts, papers, web pages, captions, and comments.

**Planning guidance**

- Wrap paper text, abstracts, web snippets, search results, and PDF-extracted text before any LLM prompt.
- Store LLM outputs only after Pydantic/schema validation.

## Test Patterns

**Likely files**

- `backend/tests/test_ground_truth_schemas.py`
- `backend/tests/test_ground_truth_clients.py`
- `backend/tests/test_ground_truth_discovery.py`
- `backend/tests/test_paper_processing.py`
- `backend/tests/test_ground_truth_persistence.py`
- `backend/tests/test_ground_truth_api.py`
- `backend/tests/test_ground_truth_e2e.py`

**Closest existing analogs**

- `backend/tests/test_research_basis.py` uses deterministic local text fixtures.
- `backend/tests/test_ingestion_api.py` monkeypatches adapter functions and validates route payloads.
- `backend/tests/test_ingestion_e2e.py` uses temporary vault roots and avoids leaving raw media in the repo.

**Planning guidance**

- Use fixtures for provider responses.
- Use temporary vault roots for raw PDF and Markdown write tests.
- Use fake repositories for MongoDB/Qdrant until integration tests explicitly need clients.
