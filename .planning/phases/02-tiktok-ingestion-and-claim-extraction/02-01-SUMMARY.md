---
phase: 02-tiktok-ingestion-and-claim-extraction
plan: "01"
subsystem: backend
tags: [fastapi, pydantic, vault, uuid, ingestion]
requires:
  - phase: 01-foundation-and-knowledge-store-contracts
    provides: UUID schemas, vault path conventions, pipeline status vocabulary
provides:
  - Phase 2 ingestion job, artifact, transcript, screenshot, and triage DTOs
  - Phase 2 extracted-claim DTO with pending-only evidence status
  - Transcript, screenshot, and raw artifact vault folder contracts
affects: [phase-2-ingestion, backend-api, frontend-ingestion, vault]
tech-stack:
  added: []
  patterns: [Pydantic DTO contracts, UUID-first artifacts, slug-only vault paths]
key-files:
  created:
    - backend/app/schemas/ingestion.py
    - backend/app/schemas/claims.py
    - backend/tests/test_ingestion_schemas.py
  modified:
    - backend/app/schemas/__init__.py
    - backend/app/contracts/vault.py
    - backend/tests/test_contracts.py
    - vault/SCHEMA.md
key-decisions:
  - "Kept job UUID separate from video, transcript, screenshot, and claim UUIDs."
  - "Added SourceKind so uploaded videos and TikTok URLs can share one job contract."
  - "Constrained Phase 2 claim evidence status to pending."
patterns-established:
  - "IngestionJob carries source_kind plus source_url/local alias, ordered stages, artifact statuses, and optional video UUID."
  - "Raw media assets live under vault/raw/{kind}/ while wiki notes stay under vault/wiki/{entity-folder}/."
requirements-completed: [ING-02, ING-05, CLM-02, CLM-03]
duration: 18min
completed: 2026-04-18
---

# Phase 2 Plan 01 Summary

**Pydantic ingestion contracts and vault artifact paths for URL, uploaded-video, transcript, screenshot, and claim artifacts**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-18T11:48:00Z
- **Completed:** 2026-04-18T12:05:54Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added `backend/app/schemas/ingestion.py` with lifecycle, stage, source-kind, artifact, transcript, screenshot, and research-basis DTOs.
- Added `backend/app/schemas/claims.py` with `ExtractedClaim` and a pending-only `EvidenceStatus`.
- Extended vault contracts and docs for transcript/screenshot wiki notes plus raw video/transcript/screenshot artifacts.

## Task Commits

1. **Task 1: Add ingestion job and artifact schemas** - included in plan commit.
2. **Task 2: Add Phase 2 claim schemas with pending evidence status** - included in plan commit.
3. **Task 3: Close transcript and screenshot vault contract gap** - included in plan commit.

## Files Created/Modified

- `backend/app/schemas/ingestion.py` - Phase 2 job, stage, artifact, transcript, screenshot, and research-basis schemas.
- `backend/app/schemas/claims.py` - Extracted claim schema and pending-only evidence status.
- `backend/tests/test_ingestion_schemas.py` - Schema coverage for enum values, uploaded-video jobs, transcript artifacts, and UUID validation.
- `backend/app/contracts/vault.py` - Raw artifact path helper and transcript/screenshot vault folders.
- `backend/tests/test_contracts.py` - Updated vault folder/path tests.
- `vault/SCHEMA.md` - Human-readable vault folder and frontmatter guidance.

## Decisions Made

- Added `SourceKind` rather than overloading `source_url` alone; uploaded videos still carry a local alias such as `uploaded://fixture.mp4`.
- Kept `validate_url` as the first stage name for compatibility with existing Phase 2 progress plans, while the stage can validate URL or upload metadata.
- Stored raw artifact paths separately from wiki note paths to keep immutable media inputs distinct from generated Markdown.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope creep.

## Issues Encountered

- `uv run` needed access to the local uv cache outside the workspace sandbox. The command was rerun with approved `uv run` escalation and passed.

## Verification

- `cd backend && uv run pytest tests/test_ingestion_schemas.py tests/test_contracts.py -q` -> 13 passed.
- `grep -q "class IngestionJob" backend/app/schemas/ingestion.py` -> passed.
- `grep -q "class ExtractedClaim" backend/app/schemas/claims.py` -> passed.
- `grep -q "transcripts" backend/app/contracts/vault.py` -> passed.
- `grep -q "vault/wiki/screenshots/" vault/SCHEMA.md` -> passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 can implement compliance-gated adapters, transcript normalization, and keyframe placeholder behavior against stable schemas and vault paths.

---
*Phase: 02-tiktok-ingestion-and-claim-extraction*
*Completed: 2026-04-18*
