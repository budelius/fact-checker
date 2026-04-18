---
phase: 04-evidence-evaluation-and-fact-check-reports
plan: "05"
subsystem: frontend-report-ui
tags: [react, typescript, reports, provenance]

requires:
  - phase: 04-evidence-evaluation-and-fact-check-reports
    provides: Report API from 04-04.
provides:
  - Typed frontend clients for ground-truth and report routes.
  - Report generation workflow from ingestion to ground truth to evaluation.
  - Report UI for narrative, claim labels, citations, evidence snippets, versions, and provenance.
affects: [docs, final-verification]

tech-stack:
  added:
    - "@types/react"
    - "@types/react-dom"
  patterns: [typed fetch clients, lifted active report state, right-rail provenance]

key-files:
  created:
    - frontend/src/api/groundTruth.ts
    - frontend/src/api/reports.ts
    - frontend/src/components/reports/ReportGenerationPanel.tsx
    - frontend/src/components/reports/ReportStatusHeader.tsx
    - frontend/src/components/reports/ReportProgressTimeline.tsx
    - frontend/src/components/reports/NarrativeReport.tsx
    - frontend/src/components/reports/ClaimEvaluationList.tsx
    - frontend/src/components/reports/ClaimEvaluationRow.tsx
    - frontend/src/components/reports/CitationList.tsx
    - frontend/src/components/reports/EvidenceSnippet.tsx
    - frontend/src/components/reports/ReportProvenancePanel.tsx
    - frontend/src/components/reports/ReportVersionList.tsx
  modified:
    - frontend/src/api/ingestion.ts
    - frontend/src/components/AppShell.tsx
    - frontend/src/components/IngestionWorkbench.tsx
    - frontend/src/styles/app.css
    - frontend/package.json
    - frontend/yarn.lock

key-decisions:
  - "Report labels are rendered from backend payloads only; the UI does not compute verdicts."
  - "Generate report starts Phase 3 ground-truth discovery first when the workbench only has an ingestion job."
  - "The right rail switches from sample note metadata to report provenance when a report is active."
  - "React type declarations were added so strict TypeScript verification can run."

patterns-established:
  - "Frontend API clients mirror backend route-local job payloads with narrow exported types."
  - "Report display components are split by status, progress, narrative, claim rows, evidence, versions, and provenance."
  - "All long UUIDs, URLs, chunk IDs, claim text, and evidence excerpts use wrapping rules."

requirements-completed:
  - UI-02
  - EVAL-01
  - EVAL-02
  - EVAL-03
  - EVAL-04
  - EVAL-05

duration: 7 min
completed: 2026-04-18
---

# Phase 4 Plan 05: Frontend Report UI Summary

**React workbench flow for generating, rerunning, and inspecting fact-check reports**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-18T14:51:10Z
- **Completed:** 2026-04-18T14:58:34Z
- **Tasks:** 4 completed
- **Files modified:** 18

## Accomplishments

- Added typed frontend clients for `/ground-truth` and `/reports`.
- Added report UI components for job status, progress, narrative summary, claim evaluations, citations, evidence snippets, version history, and provenance.
- Integrated report generation into the existing ingestion workbench.
- Added rerun handling that creates a new report version through the backend.
- Updated `AppShell` so the topbar shows `Fact-check report` and the right rail shows report provenance for the active report.
- Added responsive styling for all report label states, evidence snippets, long identifiers, and the provenance rail.
- Added React type declarations so strict TypeScript compilation succeeds.

## Task Commits

1. **Task 1: Add frontend API clients and types** - `0ca1ba2` (`feat(04-05): add report frontend clients`)
2. **Task 2: Add report display components** - `827c05c` (`feat(04-05): add report display components`)
3. **Task 3/4: Integrate report workflow and styling** - `66ce0af` (`feat(04-05): wire report workflow UI`)
4. **Type verification support** - `c9aaaa8` (`chore(frontend): add react type declarations`)

## Files Created/Modified

- `frontend/src/api/groundTruth.ts` - Ground-truth job client and payload types.
- `frontend/src/api/reports.ts` - Report job, report version, claim evaluation, citation, and evidence types.
- `frontend/src/api/ingestion.ts` - Exports shared `API_BASE_URL`.
- `frontend/src/components/reports/*` - Report viewing, evidence, provenance, and version components.
- `frontend/src/components/IngestionWorkbench.tsx` - Runs ground-truth then report generation and reruns.
- `frontend/src/components/AppShell.tsx` - Tracks active report and switches the right rail.
- `frontend/src/styles/app.css` - Report layout, label state, evidence, version, and provenance styles.
- `frontend/package.json`, `frontend/yarn.lock` - React type declarations.

## Decisions Made

- The frontend starts a ground-truth job only when it does not already have one matching the current ingestion job.
- A failed report job is rendered as a recoverable UI error and no report is selected.
- Report provenance is tied to the active report object lifted to `AppShell`.
- Strict TypeScript verification is now available through `yarn tsc --noEmit`.

## Deviations from Plan

- Added `@types/react` and `@types/react-dom` because `yarn tsc --noEmit` could not validate JSX without them.

---

**Total deviations:** 1 auto-fixed.
**Impact on plan:** Improves verification fidelity; no scope change.

## Issues Encountered

- Initial `yarn add -D @types/react @types/react-dom` failed inside the sandbox because registry DNS was blocked. It succeeded after approved network escalation.

## User Setup Required

- Run `yarn install` in `frontend/` if working from a fresh checkout to install the newly declared React type packages.

## Verification

- `cd frontend && yarn build` - passed.
- `cd frontend && yarn tsc --noEmit` - passed.
- `rg -n "Generate report|Rerun report|Fact-check report" frontend/src` - passed.
- `rg -n "supported|contradicted|mixed|insufficient" frontend/src/components frontend/src/styles/app.css` - passed.
- `rg -n "Paper summaries are navigation only" frontend/src` - passed.

## Self-Check: PASSED

Plan acceptance criteria are met. Users can generate a report from the workbench, inspect narrative-first report output, view evidence and provenance, and rerun report generation for new versions.

## Next Phase Readiness

Plan 04-06 can update documentation, requirements tracking, roadmap state, and run final Phase 4 verification.

---
*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Completed: 2026-04-18*
