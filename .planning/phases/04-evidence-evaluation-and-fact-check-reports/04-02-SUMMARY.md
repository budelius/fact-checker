---
phase: 04-evidence-evaluation-and-fact-check-reports
plan: "02"
subsystem: backend-evaluation
tags: [evidence-selection, openai, validation, prompts]

requires:
  - phase: 04-evidence-evaluation-and-fact-check-reports
    provides: Evaluation contracts from 04-01.
provides:
  - Per-claim raw evidence retrieval sets.
  - Prompt and evaluator provider boundary for structured claim evaluations.
  - Deterministic citation validation before persistence.
  - Evaluation progress helpers for the report UI/API.
affects: [reports-api, report-persistence, frontend-report-ui]

tech-stack:
  added: []
  patterns: [untrusted source wrapping, provider boundary, post-model validation gate]

key-files:
  created:
    - backend/app/evaluation/__init__.py
    - backend/app/evaluation/evidence.py
    - backend/app/evaluation/prompts.py
    - backend/app/evaluation/evaluator.py
    - backend/app/evaluation/validation.py
    - backend/app/evaluation/progress.py
    - backend/tests/test_evaluation_evidence.py
    - backend/tests/test_evaluation_evaluator.py
    - backend/tests/test_evaluation_validation.py
  modified:
    - backend/tests/test_evaluation_schemas.py

key-decisions:
  - "Paper summaries are excluded from candidate evidence and rejected as verdict citations."
  - "A deterministic evaluator is available for tests and no-paper fallback paths."
  - "Model output is validated after structured output parsing and before report persistence."

patterns-established:
  - "ClaimEvidenceSet groups cited candidates, unused candidates, and missing-evidence notes by claim UUID."
  - "OpenAI evaluator remains behind a provider class; tests use fake or deterministic evaluators."
  - "Citation validation returns typed EvaluationValidationError records and raises only at the pipeline boundary."

requirements-completed:
  - EVAL-01
  - EVAL-02
  - EVAL-03
  - EVAL-04

duration: 7 min
completed: 2026-04-18
---

# Phase 4 Plan 02: Evidence Selection and Evaluator Core Summary

**Raw evidence retrieval, schema-bound evaluator output, and deterministic citation validation for claim reports**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-18T14:33:20Z
- **Completed:** 2026-04-18T14:40:09Z
- **Tasks:** 4 completed
- **Files modified:** 10

## Accomplishments

- Built per-claim evidence selection from selected Phase 3 paper chunks and preserved unused/rejected candidates for provenance.
- Added prompt construction that wraps claims, transcript excerpts, screenshots, and evidence text as untrusted content.
- Added deterministic and OpenAI-backed evaluator classes, with fake evaluator support for tests.
- Added validation that blocks uncited non-insufficient labels, out-of-set citations, summary citations, duplicates, and missing evaluations.
- Added progress helpers for the seven Phase 4 report-generation steps.

## Task Commits

1. **Task 1: Build per-claim evidence retrieval sets** - `71d4e74` (`feat(04-02): select claim evidence sets`)
2. **Task 2: Add prompt builder and evaluator provider boundary** - `fbe498d` (`feat(04-02): add claim evaluation provider`)
3. **Task 3: Add deterministic citation validation** - `a208190` (`feat(04-02): validate claim evaluation citations`)
4. **Task 4: Add evaluation progress helpers** - `6b74fe7` (`feat(04-02): add evaluation progress helpers`)

## Files Created/Modified

- `backend/app/evaluation/evidence.py` - Per-claim evidence selection and no-direct-evidence notes.
- `backend/app/evaluation/prompts.py` - Untrusted-input-safe prompt construction.
- `backend/app/evaluation/evaluator.py` - Deterministic, fake, and OpenAI evaluator provider boundary.
- `backend/app/evaluation/validation.py` - Citation and claim coverage validation.
- `backend/app/evaluation/progress.py` - Evaluation stage helpers and log events.
- `backend/tests/test_evaluation_evidence.py` - Evidence selector coverage.
- `backend/tests/test_evaluation_evaluator.py` - Prompt/evaluator coverage without network calls.
- `backend/tests/test_evaluation_validation.py` - Validation failure and success cases.
- `backend/tests/test_evaluation_schemas.py` - Progress helper coverage.

## Decisions Made

- No-paper/no-chunk cases are represented as `insufficient` with missing-evidence notes.
- Mixed labels use citations plus rationale; semantic graph edge handling is deferred to persistence.
- OpenAI structured output is parsed into `ClaimEvaluation`, then validated independently instead of trusted directly.

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

- `cd backend && uv run pytest tests/test_evaluation_evidence.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_evaluator.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_validation.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_schemas.py tests/test_evaluation_validation.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_evidence.py tests/test_evaluation_evaluator.py tests/test_evaluation_validation.py -q` - passed.
- `rg -n "wrap_untrusted_text" backend/app/evaluation` - passed.
- `rg -n "Paper summaries are navigation only|insufficient" backend/app/evaluation` - passed.
- `rg -n "supported|contradicted|mixed" backend/tests/test_evaluation_validation.py` - passed.

## Self-Check: PASSED

Plan acceptance criteria are met. Evaluations now have a bounded evidence set, provider-isolated generation, and deterministic validation before persistence.

## Next Phase Readiness

Plan 04-03 can write validated evaluations into versioned Markdown and MongoDB relationships.

---
*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Completed: 2026-04-18*
