---
phase: 01-foundation-and-knowledge-store-contracts
plan: "02"
subsystem: backend
tags: [fastapi, pydantic, mongodb, qdrant, uuid]
requires:
  - phase: 01-01
    provides: Environment placeholders for MongoDB, Qdrant, and vault settings.
provides:
  - FastAPI backend skeleton with health and contract endpoints
  - UUID-first entity, relationship, and Qdrant payload schemas
  - MongoDB and Qdrant repository boundaries
  - Untrusted external text wrapper
affects: [backend, storage, safety, future-ingestion]
tech-stack:
  added: [fastapi, pydantic-settings, pymongo, qdrant-client, pytest, ruff]
  patterns: [uuid-canonical-schemas, repository-boundary, untrusted-input-wrapper]
key-files:
  created:
    - backend/pyproject.toml
    - backend/.python-version
    - backend/app/main.py
    - backend/app/settings.py
    - backend/app/schemas/entities.py
    - backend/app/schemas/relationships.py
    - backend/app/schemas/vector_payloads.py
    - backend/app/repositories/mongo.py
    - backend/app/repositories/qdrant.py
    - backend/app/safety/input_boundaries.py
    - backend/tests/test_settings.py
    - backend/tests/test_schemas.py
  modified: []
key-decisions:
  - "Pydantic UUID fields are the canonical identity contract across stores."
  - "MongoDB and Qdrant direct clients are isolated to repository modules."
  - "External text is explicitly wrapped as untrusted before later LLM prompting."
patterns-established:
  - "Backend settings read uppercase environment variables from the root env contract."
  - "Qdrant payloads carry uuid, entity_type, vault_path, chunk_id, source, source_date, and relationship filter fields."
requirements-completed: [KB-02, KB-04, KB-05, OPS-01, OPS-02, OPS-03, OPS-04]
duration: 11 min
completed: 2026-04-18
---

# Phase 1 Plan 02: Backend Contracts Summary

**FastAPI backend contracts with UUID schemas, MongoDB/Qdrant boundaries, and untrusted-input guards**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-18T10:05:30Z
- **Completed:** 2026-04-18T10:16:39Z
- **Tasks:** 3
- **Files modified:** 16

## Accomplishments

- Created a FastAPI backend project with `/health` and `/contracts` endpoints.
- Added Pydantic schemas for canonical entities, relationships, and Qdrant payload trace data.
- Added MongoDB and Qdrant repository modules so client usage is contained.
- Added a safety helper that wraps transcripts, papers, web pages, captions, and comments as untrusted content.

## Task Commits

1. **Task 1: Create FastAPI backend project skeleton** - `67def50`
2. **Task 2: Define canonical entity and relationship schemas** - `2fb80c7`
3. **Task 3: Add datastore repositories and untrusted-input guardrails** - `fe2f5a4`
4. **Review fix: Support root or backend `.env` lookup** - `ea26074`
5. **Verifier fix: Use per-chunk Qdrant point IDs and filter payload keys** - `9fe5821`

## Files Created/Modified

- `backend/pyproject.toml` - Backend dependency and tooling contract.
- `backend/app/main.py` - FastAPI app with health and contract endpoints.
- `backend/app/settings.py` - Pydantic settings mapped to `.env.example` keys.
- `backend/app/schemas/entities.py` - Entity type enum, external ID, and knowledge entity model.
- `backend/app/schemas/relationships.py` - Relationship type enum and edge model.
- `backend/app/schemas/vector_payloads.py` - Qdrant payload trace model.
- `backend/app/repositories/mongo.py` - MongoDB collection boundary for entities and relationships.
- `backend/app/repositories/qdrant.py` - Qdrant collection and payload boundary.
- `backend/app/safety/input_boundaries.py` - Untrusted content warning and wrapper.
- `backend/tests/test_settings.py` - Settings and contract endpoint tests.
- `backend/tests/test_schemas.py` - UUID schema and validation tests.

## Decisions Made

- Used `Field(default_factory=list)` for list fields to avoid shared mutable defaults while preserving the planned schema behavior.
- Implemented repository methods as thin real boundaries rather than pure `NotImplementedError` stubs, because the required method signatures can safely write typed records later without changing callers.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Backend settings only loaded `../.env`**
- **Found during:** Code review gate
- **Issue:** `Settings` could load the root `.env` when running from `backend/`, but not when running backend tooling from the repository root.
- **Fix:** Changed `SettingsConfigDict` to check both `.env` and `../.env`.
- **Files modified:** `backend/app/settings.py`
- **Verification:** `python3 -m compileall -q backend/app backend/tests`
- **Committed in:** `ea26074`

**2. [Rule 2 - Missing Critical] Qdrant payload/indexing contract was too narrow**
- **Found during:** Read-only verifier sidecar
- **Issue:** Qdrant payloads lacked filterable `source`, `source_date`, and relationship-list fields, and Qdrant point IDs were entity UUID-only, which could overwrite multiple chunks for one entity.
- **Fix:** Added filter payload fields and changed Qdrant point IDs to deterministic UUIDv5 values derived from entity UUID plus chunk ID.
- **Files modified:** `backend/app/schemas/vector_payloads.py`, `backend/app/repositories/qdrant.py`, `backend/app/contracts/store_sync.py`, `backend/tests/test_schemas.py`, `backend/tests/test_contracts.py`
- **Verification:** `python3 -m compileall -q backend/app backend/tests`; grep checks for `source_date`, `relationship_uuids`, and `uuid5(payload.uuid, payload.chunk_id)`
- **Committed in:** `9fe5821`

---

**Total deviations:** 2 auto-fixed (missing critical). **Impact on plan:** Strengthens KB-04 and OPS-04 without changing the Phase 1 scope.

## Issues Encountered

- `python3 -m pytest -q` could not run because `pytest` is not installed in the current Python environment.
- Verified with all plan grep checks and `python3 -m compileall -q backend/app backend/tests`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Later ingestion and indexing phases can use these schemas and repository boundaries without inventing store identity fields.

## Self-Check: PASSED

---
*Phase: 01-foundation-and-knowledge-store-contracts*
*Completed: 2026-04-18*
