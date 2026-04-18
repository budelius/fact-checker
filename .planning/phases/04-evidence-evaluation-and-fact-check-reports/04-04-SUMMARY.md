---
phase: 04-evidence-evaluation-and-fact-check-reports
plan: "04"
subsystem: backend-api
tags: [fastapi, reports, pipeline, e2e]

requires:
  - phase: 04-evidence-evaluation-and-fact-check-reports
    provides: Evaluator core from 04-02 and report persistence from 04-03.
provides:
  - EvaluationPipeline orchestration from ground-truth jobs to report versions.
  - `/reports` API routes for starting, fetching, and rerunning report jobs.
  - API-level E2E fixture with two claims, citations, unused evidence, and summary exclusion.
affects: [frontend-report-ui, docs, final-verification]

tech-stack:
  added: []
  patterns: [FastAPI route-local job store, dependency overrides, validation-before-persistence]

key-files:
  created:
    - backend/app/evaluation/indexing.py
    - backend/app/evaluation/pipeline.py
    - backend/app/api/reports.py
    - backend/tests/test_evaluation_e2e.py
    - backend/tests/test_reports_api.py
  modified:
    - backend/app/main.py

key-decisions:
  - "The report API starts from a stored Phase 3 ground-truth job and loads the matching ingestion claims."
  - "Validation failure returns a failed EvaluationJob and prevents Markdown/MongoDB persistence."
  - "Report reruns reuse prior versions to compute the next version instead of overwriting."

patterns-established:
  - "EvaluationPipeline composes evidence selection, evaluator, validation, report versioning, persistence, and optional indexing."
  - "Reports API mirrors the Phase 3 job-store route pattern."
  - "No-paper workflows produce insufficient-evidence reports through the deterministic evaluator."

requirements-completed:
  - EVAL-01
  - EVAL-02
  - EVAL-03
  - EVAL-04
  - EVAL-05

duration: 6 min
completed: 2026-04-18
---

# Phase 4 Plan 04: Report API and Pipeline Summary

**FastAPI report workflow from Phase 3 ground truth to validated, versioned fact-check reports**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-18T14:44:51Z
- **Completed:** 2026-04-18T14:50:55Z
- **Tasks:** 3 completed
- **Files modified:** 6

## Accomplishments

- Added `EvaluationPipeline` to run claim loading, evidence selection, evaluation, validation, Markdown/MongoDB persistence, and optional indexing.
- Added `/reports/jobs/from-ground-truth/{ground_truth_job_uuid}`, rerun, job fetch, and report fetch routes.
- Wired the reports router into FastAPI.
- Added backend E2E tests for cited reports, no-paper insufficient reports, validation failure, and API-level two-claim report generation.

## Task Commits

1. **Task 1: Add evaluation pipeline orchestration** - `4a54d90` (`feat(04-04): orchestrate evaluation pipeline`)
2. **Task 2: Add reports API router** - `5a98c7a` (`feat(04-04): add report job API`)
3. **Task 3: Add API-level E2E fixture** - `3288a00` (`test(04-04): cover report API e2e`)

## Files Created/Modified

- `backend/app/evaluation/pipeline.py` - Composes the Phase 4 backend workflow.
- `backend/app/evaluation/indexing.py` - Optional report indexing stub; paper chunks remain the verdict evidence index.
- `backend/app/api/reports.py` - Report job and report fetch/rerun routes.
- `backend/app/main.py` - Includes the reports router.
- `backend/tests/test_evaluation_e2e.py` - Pipeline E2E tests.
- `backend/tests/test_reports_api.py` - Report API and API-level E2E tests.

## Decisions Made

- Report generation fails before persistence when citation validation fails.
- Base report generation also uses previous versions when present, so repeated calls create a new version rather than colliding.
- Optional report indexing is skipped for Phase 4; source chunk indexing from Phase 3 remains the retrieval base.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope change.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Verification

- `cd backend && uv run pytest tests/test_evaluation_e2e.py -q` - passed.
- `cd backend && uv run pytest tests/test_reports_api.py -q` - passed.
- `cd backend && uv run pytest tests/test_reports_api.py tests/test_evaluation_e2e.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_schemas.py tests/test_evaluation_evidence.py tests/test_evaluation_validation.py tests/test_evaluation_markdown.py tests/test_evaluation_persistence.py -q` - passed.
- `rg -n "include_router.*reports|reports_router" backend/app/main.py backend/app/api/reports.py` - passed.
- `rg -n "ground_truth_job_not_found|validation" backend/app/api/reports.py backend/app/evaluation/pipeline.py` - passed.

## Self-Check: PASSED

Plan acceptance criteria are met. The backend can generate and fetch report jobs from stored Phase 3 ground-truth jobs with validation and versioning.

## Next Phase Readiness

Plan 04-05 can consume `/reports` payloads in the React workbench.

---
*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Completed: 2026-04-18*
