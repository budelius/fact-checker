# Phase 4: Evidence Evaluation and Fact-Check Reports - Pattern Map

**Mapped:** 2026-04-18
**Status:** Ready for planning
**Source:** Local orchestrator fallback; no pattern-mapper subagent used in this run.

## Purpose

This file maps Phase 4 implementation areas to existing repo analogs and contracts. It is a planner input only; `04-CONTEXT.md`, `04-UI-SPEC.md`, and `04-RESEARCH.md` remain authoritative for scope and technical decisions.

## Backend Patterns

### API Router

**Likely files**

- `backend/app/api/reports.py`
- `backend/app/main.py`

**Closest existing analog**

- `backend/app/api/ground_truth.py` defines a route-local job store, dependency builders, a `POST /jobs/from-ingestion/{uuid}` route, and a `GET /jobs/{uuid}` route.
- `backend/app/main.py` wires routers with `app.include_router(...)`.

**Planning guidance**

- Add a separate `reports` router rather than extending `ground_truth`.
- Start report jobs from `GroundTruthJob` UUIDs so Phase 4 consumes Phase 3 artifacts explicitly.
- Recommended routes:
  - `POST /reports/jobs/from-ground-truth/{ground_truth_job_uuid}`
  - `GET /reports/jobs/{job_uuid}`
  - `GET /reports/{report_uuid}`
  - Optional rerun alias: `POST /reports/jobs/from-ground-truth/{ground_truth_job_uuid}/rerun`

### Pydantic Schemas

**Likely files**

- `backend/app/schemas/evaluation.py`
- `backend/app/schemas/claims.py`
- `backend/app/schemas/__init__.py`

**Closest existing analog**

- `backend/app/schemas/ground_truth.py` uses enums, UUID defaults, nested stage objects, artifact objects, and `Field(default_factory=list)`.
- `backend/app/schemas/claims.py` currently keeps evidence status pending through Phase 3.

**Planning guidance**

- Add a dedicated `EvaluationLabel` enum for `supported`, `contradicted`, `mixed`, and `insufficient`.
- Keep Phase 2 and Phase 3 claim defaults as `pending`; label output should live in report/evaluation payloads.
- Add stage names for report generation: load claims, load evidence, select citations, evaluate claims, validate citations, write report, index and link.

### Evaluation Service

**Likely files**

- `backend/app/evaluation/evidence.py`
- `backend/app/evaluation/prompts.py`
- `backend/app/evaluation/evaluator.py`
- `backend/app/evaluation/validation.py`
- `backend/app/evaluation/progress.py`

**Closest existing analog**

- `backend/app/ground_truth/summarization.py` uses OpenAI Responses structured outputs with a strict JSON schema and a deterministic fallback.
- `backend/app/safety/input_boundaries.py` provides `wrap_untrusted_text(...)`.

**Planning guidance**

- Keep the LLM provider behind a small class or protocol.
- Tests should use fake evaluator output and should not require `OPENAI_API_KEY`.
- Run a deterministic validator after every evaluator response.
- Treat summaries as navigation metadata only; do not pass them as evidence or allow them as citations.

### Evidence Selection

**Likely files**

- `backend/app/evaluation/evidence.py`
- `backend/tests/test_evaluation_evidence.py`

**Closest existing analog**

- `backend/app/ground_truth/pipeline.py` already maps selected `SourceDecision` records to candidate papers and chunks.
- `backend/app/schemas/ground_truth.py` provides `SourceDecision`, `PaperMetadata`, and `PaperChunk`.

**Planning guidance**

- Build a per-claim retrieval set from selected source decisions and chunks.
- Include paper metadata, source links, preprint status, chunk UUIDs, and chunk text.
- Include rejected/unused candidates in provenance, but mark them as candidates, not citations.
- Handle no-paper/no-chunk jobs by generating `insufficient` evaluations.

### Markdown And Persistence

**Likely files**

- `backend/app/evaluation/markdown.py`
- `backend/app/evaluation/persistence.py`
- `backend/app/repositories/mongo.py`
- `vault/templates/report.md`

**Closest existing analog**

- `backend/app/ground_truth/markdown.py` builds vault Markdown.
- `backend/app/ground_truth/persistence.py` writes paper Markdown and Mongo entities/relationships.
- `vault/templates/report.md` already reserves a report note format.

**Planning guidance**

- Expand `vault/templates/report.md` to match the Phase 4 report sections.
- Persist a `report` entity with a stable vault path.
- For supported/contradicted labels, write `supports`/`contradicts` relationships from claim to evidence where semantically valid.
- For mixed labels, cite evidence and store the mixed rationale/provenance without creating a misleading single relationship.
- For insufficient labels, write report provenance but no support/contradiction relationship.

### Qdrant

**Likely files**

- `backend/app/evaluation/indexing.py` if report indexing is implemented
- `backend/app/schemas/vector_payloads.py`

**Closest existing analog**

- `backend/app/ground_truth/indexing.py` indexes chunks and summaries through an embedding provider.
- `backend/app/repositories/qdrant.py` uses deterministic point IDs from payload UUID and chunk ID.

**Planning guidance**

- Report indexing is optional for Phase 4 if the report is already persisted in Markdown and MongoDB.
- If implemented, index the narrative report and claim rationale as report chunks with `entity_type=report`, report UUID, vault path, and cited relationship UUIDs.

### Pipeline Logging

**Likely files**

- `backend/app/evaluation/progress.py`
- `backend/app/contracts/logging.py`

**Closest existing analog**

- `backend/app/contracts/logging.py` already includes `evaluation` as an allowed event type.
- Phase 2/3 stages use stable step names and lifecycle statuses.

**Planning guidance**

- Each report job should expose named stages and the current operation.
- Preserve failed stages and UUIDs for transparent reruns.
- Log citation validation failures explicitly.

## Frontend Patterns

### API Client

**Likely files**

- `frontend/src/api/reports.ts`

**Closest existing analog**

- `frontend/src/api/ingestion.ts` declares API types, parses HTTP errors, and exposes small route helpers.

**Planning guidance**

- Mirror backend `EvaluationJob`, `ReportVersion`, `ClaimEvaluation`, and citation payloads.
- Keep report label types narrow in TypeScript.
- Reuse the same `API_BASE_URL` environment style.

### Workbench Integration

**Likely files**

- `frontend/src/components/IngestionWorkbench.tsx`
- `frontend/src/components/reports/*`
- `frontend/src/styles/app.css`

**Closest existing analog**

- `frontend/src/components/ingestion/ProgressTimeline.tsx` renders stage progress.
- `frontend/src/components/ingestion/ClaimExtractionList.tsx` renders claim rows.
- `frontend/src/components/MetadataPanel.tsx` owns right-rail metadata style.

**Planning guidance**

- Add report generation after ingestion/ground-truth completion.
- Render backend progress stages using a report-specific timeline or a shared stage component.
- Keep the narrative report first, then compact claim rows, then evidence/provenance.
- Use the existing token palette and label mappings from `04-UI-SPEC.md`.

### Styling

**Likely files**

- `frontend/src/styles/app.css`
- `frontend/src/styles/tokens.css`

**Closest existing analog**

- Existing ingestion panels use dense rows, bordered surfaces, tokenized colors, and responsive layouts.

**Planning guidance**

- Add label chip classes for supported, contradicted, mixed, and insufficient.
- Use stable dimensions and `overflow-wrap: anywhere` for claim text, UUIDs, URLs, and chunk IDs.
- Do not add a new UI framework or a marketing route.

## Test Patterns

**Likely backend tests**

- `backend/tests/test_evaluation_schemas.py`
- `backend/tests/test_evaluation_evidence.py`
- `backend/tests/test_evaluation_validator.py`
- `backend/tests/test_evaluation_markdown.py`
- `backend/tests/test_evaluation_persistence.py`
- `backend/tests/test_reports_api.py`
- `backend/tests/test_evaluation_e2e.py`

**Closest existing analogs**

- `backend/tests/test_ground_truth_e2e.py` uses fake providers, repositories, embedding providers, and temporary vault roots.
- `backend/tests/test_ground_truth_api.py` uses FastAPI dependency overrides and in-memory job stores.

**Planning guidance**

- No live network calls in tests.
- Use fixtures for supported, contradicted, mixed/overclaim, insufficient/no-paper, and news-exception cases.
- Assert that non-insufficient labels without citations fail validation.
- Assert that paper summary UUIDs cannot be used as citations.

**Likely frontend verification**

- `cd frontend && yarn build`

If frontend tests are added later, include rendering fixtures for all four labels and mobile-safe long-text cases.
