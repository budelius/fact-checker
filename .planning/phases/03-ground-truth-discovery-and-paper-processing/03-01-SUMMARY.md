---
phase: 03-ground-truth-discovery-and-paper-processing
plan: "01"
subsystem: backend-contracts
tags: [ground-truth, schemas, settings, vault, logging, openai, pypdf]
requires:
  - phase: 02-tiktok-ingestion-and-claim-extraction
    provides: ingestion jobs, claims, screenshots, and research-basis hints
provides:
  - Ground-truth provider and paper processing settings
  - Shared Phase 3 candidate, decision, paper, chunk, summary, job, stage, and artifact schemas
  - Pipeline logging and raw paper vault contracts
affects: [phase-3-provider-clients, phase-3-discovery, phase-3-paper-processing, phase-3-persistence]
tech-stack:
  added: [httpx, openai, pypdf]
  patterns: [Pydantic DTO contracts, provider config via environment, immutable raw paper vault paths]
key-files:
  created:
    - backend/app/schemas/ground_truth.py
    - backend/tests/test_ground_truth_schemas.py
  modified:
    - backend/pyproject.toml
    - backend/uv.lock
    - backend/app/settings.py
    - backend/app/contracts/logging.py
    - backend/app/contracts/vault.py
    - backend/app/schemas/__init__.py
    - backend/tests/test_settings.py
    - backend/tests/test_contracts.py
    - vault/SCHEMA.md
key-decisions:
  - "Keep external paper identifiers as metadata aliases; UUIDs remain canonical."
  - "Use explicit no_paper_found and supplemental statuses so non-paper sources cannot become v1 ground truth."
  - "Add raw paper storage only for lawfully public PDFs; paywalled or unavailable papers stay linked or metadata-only."
patterns-established:
  - "GroundTruthJob tracks stages, artifacts, candidates, decisions, papers, chunks, and summaries as typed Pydantic records."
  - "Phase 3 trace events use source_discovery, paper_processing, and summarization event types."
requirements-completed:
  - SRC-03
  - SRC-04
  - SRC-05
  - PPR-01
  - PPR-02
  - PPR-03
  - PPR-04
  - PPR-05
duration: 20 min
completed: 2026-04-18
---

# Phase 3 Plan 01: Contract Foundation Summary

**Ground-truth schema, settings, logging, and raw-paper vault contracts for Phase 3 provider and paper processing work**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-18T13:00:00Z
- **Completed:** 2026-04-18T13:20:01Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added runtime dependencies and environment-backed configuration for OpenAI, paper-index providers, embeddings, and PDF handling.
- Added `backend/app/schemas/ground_truth.py` with typed candidates, source decisions, paper metadata, acquisition, chunks, summaries, job stages, and artifacts.
- Extended pipeline logging and vault contracts so Phase 3 can trace source discovery, paper processing, summarization, and raw public PDF storage.

## Task Commits

1. **Task 1: Add Phase 3 runtime dependencies and settings** - `2d5b210`
2. **Task 2: Add ground-truth schemas** - `70e8581`
3. **Task 3: Extend logging and vault contracts for paper processing** - `f94ca3e`

## Files Created/Modified

- `backend/app/schemas/ground_truth.py` - Shared DTOs and enums for Phase 3 jobs, candidates, decisions, papers, chunks, and summaries.
- `backend/app/settings.py` - Provider, model, embedding, and paper acquisition settings.
- `backend/app/contracts/logging.py` - Phase 3 pipeline event types.
- `backend/app/contracts/vault.py` - Raw `papers` artifact folder contract.
- `vault/SCHEMA.md` - Public-paper raw evidence storage policy.
- `backend/tests/test_settings.py` - Settings default and environment override tests.
- `backend/tests/test_ground_truth_schemas.py` - Schema and enum coverage.
- `backend/tests/test_contracts.py` - Logging and vault contract coverage.

## Decisions Made

- Used `text-embedding-3-small` as the default embedding model while keeping vector dimensions configurable/inferred later.
- Represented no-paper outcomes as explicit `CandidateStatus.no_paper_found` decisions instead of a failed job state.
- Added `GroundTruthStage` and `GroundTruthArtifact` records now so progress and traceable artifacts do not have to be retrofitted in later plans.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Verification

- `uv run pytest tests/test_settings.py tests/test_contracts.py tests/test_ground_truth_schemas.py -q` passed: 21 tests.
- `git diff --check` passed for the Wave 1 files.

## User Setup Required

None - no external service configuration required for this plan. Later live provider use will require environment variables such as `OPENAI_API_KEY`, and optionally `OPENALEX_EMAIL` and `SEMANTIC_SCHOLAR_API_KEY`.

## Next Phase Readiness

Wave 2 can now implement provider clients and paper acquisition/parsing against stable shared schemas and contracts.

## Self-Check: PASSED

---
*Phase: 03-ground-truth-discovery-and-paper-processing*
*Completed: 2026-04-18*
