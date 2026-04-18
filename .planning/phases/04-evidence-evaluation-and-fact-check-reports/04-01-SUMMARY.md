---
phase: 04-evidence-evaluation-and-fact-check-reports
plan: "01"
subsystem: backend-contracts
tags: [pydantic, evaluation, reports, settings]

requires:
  - phase: 03-ground-truth-discovery-and-paper-processing
    provides: Paper chunks, source decisions, and ground-truth jobs consumed by evaluation.
provides:
  - Evaluation label, citation, candidate evidence, claim evaluation, report version, and evaluation job schemas.
  - Configurable OpenAI evaluation model and evidence selection limits.
affects: [backend, reports-api, frontend-report-types, phase-4]

tech-stack:
  added: []
  patterns: [Pydantic enum contracts, report-version payloads, settings aliases]

key-files:
  created:
    - backend/app/schemas/evaluation.py
    - backend/tests/test_evaluation_schemas.py
  modified:
    - backend/app/schemas/__init__.py
    - backend/app/settings.py
    - backend/tests/test_settings.py

key-decisions:
  - "Evaluation labels live in report/evaluation payloads; extracted claims still default to pending."
  - "Report versions include cited and unused candidate evidence to preserve provenance."
  - "Evaluation model and chunk/excerpt limits are configurable through environment variables."

patterns-established:
  - "EvaluationJob mirrors existing job lifecycle patterns with explicit Phase 4 stages."
  - "ReportVersion is the durable API/Markdown payload boundary for report UI and persistence."

requirements-completed:
  - EVAL-01
  - EVAL-02
  - EVAL-03
  - EVAL-04
  - EVAL-05

duration: 18 min
completed: 2026-04-18
---

# Phase 4 Plan 01: Evaluation Contracts and Settings Summary

**Typed claim evaluation and report-version contracts with configurable evaluator settings**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-18T14:15:00Z
- **Completed:** 2026-04-18T14:33:20Z
- **Tasks:** 3 completed
- **Files modified:** 5

## Accomplishments

- Added `EvaluationLabel`, `EvidenceCitation`, `EvidenceCandidate`, `ClaimEvaluation`, `ReportVersion`, and `EvaluationJob` schemas.
- Preserved the earlier `ExtractedClaim.evidence_status = pending` behavior while adding report-level labels.
- Added `OPENAI_EVALUATION_MODEL`, `EVALUATION_MAX_CHUNKS_PER_CLAIM`, and `EVALUATION_EXCERPT_MAX_CHARS` settings with tests.

## Task Commits

1. **Task 1: Add evaluation schema module** - `ff3ca6f` (`feat(04-01): add evaluation schemas`)
2. **Task 2: Preserve claim defaults while allowing evaluated status mapping** - no code commit; regression verified with existing and new tests.
3. **Task 3: Add evaluation settings** - `ad05882` (`feat(04-01): add evaluation settings`)

## Files Created/Modified

- `backend/app/schemas/evaluation.py` - Phase 4 labels, evidence records, report versions, and evaluation jobs.
- `backend/tests/test_evaluation_schemas.py` - Schema validation and claim-default regression tests.
- `backend/app/schemas/__init__.py` - Re-exported evaluation contracts.
- `backend/app/settings.py` - Added evaluator model and evidence selection limits.
- `backend/tests/test_settings.py` - Added default and environment override coverage for evaluation settings.

## Decisions Made

- Evaluation results are separate from ingestion claim defaults to avoid changing Phase 2/3 behavior.
- Evidence candidates and citations carry raw source provenance, source URLs, chunk IDs, preprint status, and source policy notes.
- Report versions are represented as first-class payloads with report UUID, report group UUID, version, Markdown path, label counts, cited evidence, and unused candidate evidence.

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

- `cd backend && uv run pytest tests/test_evaluation_schemas.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_schemas.py tests/test_ground_truth_api.py tests/test_ground_truth_e2e.py -q` - passed.
- `cd backend && uv run pytest tests/test_settings.py tests/test_evaluation_schemas.py -q` - passed.
- `cd backend && uv run pytest tests/test_ground_truth_api.py tests/test_ground_truth_e2e.py -q` - passed.
- `rg -n "class EvaluationLabel|class ClaimEvaluation|class ReportVersion|class EvaluationJob" backend/app/schemas/evaluation.py` - passed.
- `rg -n "openai_evaluation_model|evaluation_max_chunks_per_claim|evaluation_excerpt_max_chars" backend/app/settings.py` - passed.

## Self-Check: PASSED

Plan acceptance criteria are met. Phase 4 has central typed evaluation contracts and configurable evaluator settings, while earlier phase claim payloads remain pending by default.

## Next Phase Readiness

Wave 2 can now build evidence selection, evaluator validation, report Markdown, and persistence against these stable schemas.

---
*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Completed: 2026-04-18*
