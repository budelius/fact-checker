---
phase: 04-evidence-evaluation-and-fact-check-reports
plan: "03"
subsystem: backend-persistence
tags: [markdown, mongodb, graph, versioning]

requires:
  - phase: 04-evidence-evaluation-and-fact-check-reports
    provides: Evaluation schemas from 04-01.
provides:
  - Versioned fact-check report Markdown builder.
  - Rerun/version identity helpers.
  - Report entity and relationship persistence.
affects: [reports-api, markdown-vault, mongodb-graph, frontend-report-ui]

tech-stack:
  added: []
  patterns: [versioned report slugs, semantic relationship filtering, provenance appendix]

key-files:
  created:
    - backend/app/evaluation/markdown.py
    - backend/app/evaluation/versioning.py
    - backend/app/evaluation/persistence.py
    - backend/tests/test_evaluation_markdown.py
    - backend/tests/test_evaluation_persistence.py
  modified:
    - vault/templates/report.md

key-decisions:
  - "Each rerun uses a new report version/path while preserving the report group UUID."
  - "Mixed labels create cite/provenance relationships, not misleading support or contradiction edges."
  - "Insufficient labels create report discussion provenance only, not evidence conclusion edges."

patterns-established:
  - "Report Markdown contains narrative, claims, used evidence, candidate evidence reviewed, and provenance sections."
  - "Report persistence writes Markdown first, then upserts report entity and graph relationships."
  - "Rerun availability is detected by comparing known report evidence UUIDs with latest evidence UUIDs."

requirements-completed:
  - EVAL-03
  - EVAL-04
  - EVAL-05

duration: 5 min
completed: 2026-04-18
---

# Phase 4 Plan 03: Versioned Report Persistence Summary

**Versioned Markdown fact-check reports with provenance and conservative MongoDB relationship semantics**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-18T14:40:09Z
- **Completed:** 2026-04-18T14:44:51Z
- **Tasks:** 3 completed
- **Files modified:** 6

## Accomplishments

- Expanded the report template with Phase 4 frontmatter for versioning, source jobs, claims, cited evidence, candidate evidence, label counts, and provenance.
- Added a Markdown builder with narrative-first report output, claim details, evidence used, candidate evidence reviewed, and provenance sections.
- Added deterministic report version identity and rerun availability helpers.
- Added report persistence that writes Markdown, upserts a report entity, and creates graph relationships without overstating mixed/insufficient labels.

## Task Commits

1. **Task 1: Expand the report Markdown template and builder** - `55f8242` (`feat(04-03): build report markdown`)
2. **Task 2: Add report versioning** - `89d65b8` (`feat(04-03): add report versioning`)
3. **Task 3: Persist report entities and relationships** - `e2bc426` (`feat(04-03): persist report knowledge`)

## Files Created/Modified

- `backend/app/evaluation/markdown.py` - Builds Obsidian-compatible report Markdown.
- `backend/app/evaluation/versioning.py` - Computes report group/version identities and rerun availability.
- `backend/app/evaluation/persistence.py` - Writes report Markdown and MongoDB entities/relationships.
- `backend/tests/test_evaluation_markdown.py` - Markdown structure and warning coverage.
- `backend/tests/test_evaluation_persistence.py` - Versioning and graph relationship coverage.
- `vault/templates/report.md` - Expanded Phase 4 report template.

## Decisions Made

- Report slugs include the report group prefix and version number for stable historical paths.
- The report itself cites evidence; claim-level support/contradiction edges are only created for `supported` and `contradicted`.
- `mixed` labels use `cites` provenance; `insufficient` labels use `discussed_in` only.

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

- `cd backend && uv run pytest tests/test_evaluation_markdown.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_markdown.py tests/test_evaluation_persistence.py -q` - passed.
- `cd backend && uv run pytest tests/test_evaluation_persistence.py -q` - passed.
- `rg -n "Paper summaries are navigation only|Candidate evidence reviewed|Provenance" backend/app/evaluation/markdown.py vault/templates/report.md` - passed.
- `rg -n "supports|contradicts|mixed|insufficient" backend/app/evaluation/persistence.py backend/tests/test_evaluation_persistence.py` - passed.

## Self-Check: PASSED

Plan acceptance criteria are met. Report versions are stable, Markdown is traceable, and graph relationships avoid unsupported truth implications.

## Next Phase Readiness

Plan 04-04 can compose evidence selection, evaluator validation, report Markdown, and persistence into the reports API workflow.

---
*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Completed: 2026-04-18*
