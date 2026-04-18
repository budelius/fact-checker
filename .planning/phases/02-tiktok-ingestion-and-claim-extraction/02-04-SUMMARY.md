---
phase: 02-tiktok-ingestion-and-claim-extraction
plan: "04"
subsystem: backend
tags: [fastapi, uploadfile, python-multipart, ingestion-jobs, mongodb, vault]
requires:
  - phase: 02-tiktok-ingestion-and-claim-extraction
    provides: Plans 02 and 03 adapter, transcript, claim, and triage services
provides:
  - Ingestion API routes for TikTok URL, fixture transcript, video upload, and job status
  - In-memory job fallback for local tests and development
  - Local raw video upload storage under vault/raw/videos
  - Mongo repository collections for ingestion jobs and pipeline events
  - Video/transcript/screenshot/claim persistence builders
affects: [phase-2-ui, phase-2-e2e, phase-3-source-discovery]
tech-stack:
  added: [python-multipart]
  patterns: [thin FastAPI router, in-process fixture orchestration, local raw upload artifact]
key-files:
  created:
    - backend/app/api/ingestion.py
    - backend/app/ingestion/jobs.py
    - backend/app/ingestion/progress.py
    - backend/app/ingestion/uploads.py
    - backend/app/ingestion/persistence.py
    - backend/tests/test_ingestion_api.py
    - backend/tests/test_video_upload.py
    - backend/tests/test_ingestion_progress.py
    - backend/tests/test_ingestion_persistence.py
  modified:
    - backend/app/main.py
    - backend/app/repositories/mongo.py
    - backend/app/ingestion/claims.py
    - backend/pyproject.toml
    - backend/uv.lock
key-decisions:
  - "Video uploads are stored locally and response details include third_party_upload=false."
  - "Local fixture claim extraction is deterministic and keeps evidence_status pending."
  - "Uploaded-video jobs can succeed with media-only artifacts when transcript/transcription is unavailable."
patterns-established:
  - "All Phase 2 API responses expose serialized job state plus derived artifact payloads for the UI."
  - "Tests use temporary vault roots so upload tests do not leave raw media fixtures in the workspace."
requirements-completed: [ING-01, ING-02, ING-03, ING-04, ING-05, CLM-01, CLM-02, CLM-03]
duration: 28min
completed: 2026-04-18
---

# Phase 2 Plan 04 Summary

**FastAPI ingestion jobs with local video upload storage, fixture transcript orchestration, and owned artifact persistence**

## Performance

- **Duration:** 28 min
- **Started:** 2026-04-18T11:55:00Z
- **Completed:** 2026-04-18T12:23:07Z
- **Tasks:** 4
- **Files modified:** 15

## Accomplishments

- Added `POST /ingestion/tiktok`, `POST /ingestion/fixtures/transcript`, `POST /ingestion/videos/upload`, and `GET /ingestion/jobs/{job_uuid}`.
- Added local video upload validation/storage with multipart support and raw artifact details under `vault/raw/videos/`.
- Added ordered progress stages, job serialization/storage, and Mongo collection hooks for ingestion jobs and pipeline events.
- Added persistence builders for video, transcript, screenshot, claim entities, and `derived_from` relationships.

## Task Commits

1. **Task 1: Add ingestion job repository and progress service** - included in plan commit.
2. **Task 2: Add ingestion API routes** - included in plan commit.
3. **Task 3: Add persistence service for owned artifacts** - included in plan commit.
4. **Task 4: Add fixture orchestration path** - included in plan commit.

## Files Created/Modified

- `backend/app/api/ingestion.py` - Ingestion routes and local fixture/upload orchestration.
- `backend/app/ingestion/jobs.py` - Job creation, lifecycle updates, serialization, and in-memory fallback store.
- `backend/app/ingestion/progress.py` - Ordered progress stages and pipeline log builder.
- `backend/app/ingestion/uploads.py` - Video upload validation and raw vault storage.
- `backend/app/ingestion/persistence.py` - Entity and relationship builders for owned artifacts.
- `backend/tests/test_ingestion_api.py` - URL, fixture transcript, status, and upload API tests.
- `backend/tests/test_video_upload.py` - Dedicated upload behavior tests.
- `backend/tests/test_ingestion_progress.py` - Stage/progress/log tests.
- `backend/tests/test_ingestion_persistence.py` - Vault path and upsert count tests.
- `backend/pyproject.toml` and `backend/uv.lock` - Added `python-multipart`.

## Decisions Made

- Used a local deterministic fixture extractor to exercise CLM-01 without OpenAI access; extracted claims remain pending and are not evidence evaluations.
- Kept live TikTok metadata retrieval disabled in the URL route for local Phase 2 execution; fixture/upload paths prove the pipeline shape.
- Added CORS for local Vite origins so the Phase 2 React workbench can call the backend during development.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added `python-multipart` dependency**
- **Found during:** Task 2 (video upload API)
- **Issue:** FastAPI cannot import `UploadFile`/`Form` routes without multipart parser support.
- **Fix:** Ran `uv add python-multipart` and verified `import multipart`.
- **Files modified:** `backend/pyproject.toml`, `backend/uv.lock`
- **Verification:** Upload API tests passed.

**2. [Rule 2 - Missing Critical] Added deterministic fixture claim extraction**
- **Found during:** Task 4 (fixture orchestration)
- **Issue:** A provider-disabled path alone could not prove CLM-01 in local tests.
- **Fix:** Added local signal-based extraction for fixture/demo transcript paths only, preserving pending evidence status.
- **Files modified:** `backend/app/ingestion/claims.py`, `backend/app/api/ingestion.py`
- **Verification:** Fixture transcript tests assert pending claims and research-basis candidates.

---

**Total deviations:** 2 auto-fixed.
**Impact on plan:** Both changes support the requested upload/local fixture behavior without adding live provider calls or evidence labels.

## Issues Encountered

- Upload tests originally wrote fake media under the real workspace vault. Tests now set a temporary `VAULT_ROOT`, and generated raw test artifacts were removed.

## Verification

- `cd backend && uv run pytest tests/test_ingestion_api.py tests/test_video_upload.py tests/test_ingestion_progress.py tests/test_ingestion_persistence.py -q` -> 14 passed.
- `cd backend && uv run pytest -q` -> 52 passed.
- `cd backend && uv run ruff check .` -> all checks passed.
- `grep -q 'APIRouter(prefix="/ingestion"' backend/app/api/ingestion.py` -> passed.
- `grep -q 'videos/upload' backend/app/api/ingestion.py` -> passed.
- `grep -q "include_router" backend/app/main.py` -> passed.
- `grep -q "ingestion_jobs" backend/app/repositories/mongo.py` -> passed.
- `grep -q "claim_extraction_provider_disabled" backend/app/api/ingestion.py` -> passed.

## User Setup Required

None for local fixture/upload tests. Production deployments must configure persistent vault storage before accepting large uploads.

## Next Phase Readiness

The frontend can now call real backend routes for TikTok URL submission, video upload, pasted transcript fixtures, and job polling.

---
*Phase: 02-tiktok-ingestion-and-claim-extraction*
*Completed: 2026-04-18*
