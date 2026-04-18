# Roadmap: Fact Checker

**Created:** 2026-04-18
**Updated:** 2026-04-18
**Current milestone:** v1.1 Report Generation Responsiveness
**Core Value:** Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## Milestones

- Complete: **v1.0 MVP** - Phases 1-5 shipped 2026-04-18. Archive: `.planning/milestones/v1.0-ROADMAP.md`
- Planned: **v1.1 Report Generation Responsiveness** - Phases 6-9.

## v1.1 Overview

v1.1 fixes the report-generation product gap discovered after v1.0: "Generate report" can still feel broken because the UI waits while Phase 3 live paper discovery and paper processing run before Phase 4 evidence evaluation. This milestone makes that path job-oriented, bounded, recoverable, and visibly understandable.

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 6 | Report Job Lifecycle and Async Execution | Return report job identity immediately, run ground-truth/report work through pollable stages, persist status, and support safe retry after interruption. | RPT-01, RPT-02, RPT-05, OPS-05 |
| 7 | Bounded Ground-Truth and Evidence Reuse | Limit expensive UI-triggered live paper work, reuse stored evidence first, and record the limits used in report provenance. | RPT-03, RPT-04, EVAL-06, SRC-06 |
| 8 | Report Generation UX Redesign | Replace the blocking/opaque report panel with a clear workflow for starting, monitoring, recovering, reading, and rerunning reports. | UX-01, UX-02, UX-03, UX-04, UX-05 |
| 9 | v1.1 Verification and Recovery Hardening | Validate async lifecycle, polling, bounded processing, retry/rerun idempotency, error mapping, and responsive UI states end to end. | OPS-06 |

**Coverage:** 14 of 14 v1.1 requirements mapped.

## Phase Details

### Phase 6: Report Job Lifecycle and Async Execution

**Status:** Planned

**Goal:** Return report job identity immediately, run ground-truth/report work through pollable stages, persist status, and support safe retry after interruption.

**Requirements:** RPT-01, RPT-02, RPT-05, OPS-05

**UI hint:** yes

**Success Criteria:**

1. Starting a report returns a job UUID and initial status immediately, before live discovery or evaluation finishes.
2. Ground-truth discovery, paper processing, evidence evaluation, report writing, and indexing are visible as separate pollable stages.
3. Refreshing the browser can reload the active job and continue showing status.
4. Restarting the local backend does not lose completed or failed job state needed for recovery.
5. Retrying or rerunning a failed/interrupted job does not duplicate canonical Markdown, MongoDB entities, relationships, or Qdrant payloads.

**Implementation Notes:**

- Prefer a simple local durable job store that fits the current MongoDB boundary before adding external queue infrastructure.
- Keep report job state separate from generated report versions.
- Preserve compatibility with the current `/reports/jobs/{job_uuid}` polling endpoint shape where possible.

### Phase 7: Bounded Ground-Truth and Evidence Reuse

**Status:** Planned

**Goal:** Limit expensive UI-triggered live paper work, reuse stored evidence first, and record the limits used in report provenance.

**Requirements:** RPT-03, RPT-04, EVAL-06, SRC-06

**UI hint:** yes

**Success Criteria:**

1. A default UI report run has explicit limits for live providers, candidates per claim, paper downloads, parsing, summarization, and indexing.
2. The system checks existing stored claims, papers, chunks, summaries, and graph relationships before launching live discovery.
3. The user can choose a full refresh/rerun when they want a more exhaustive run.
4. Reports clearly record whether evidence came from stored knowledge, bounded live discovery, bounded paper processing, or a full refresh.
5. Claims remain `insufficient evidence` when bounded processing leaves too little evidence to support a stronger label.

**Implementation Notes:**

- Treat bounded mode as a product behavior, not only a timeout.
- Do not hide skipped work; skipped providers, candidates, or paper processing should be visible in job/report provenance.
- Preserve the v1.0 paper/preprint-only ground-truth policy.

### Phase 8: Report Generation UX Redesign

**Status:** Planned

**Goal:** Replace the blocking/opaque report panel with a clear workflow for starting, monitoring, recovering, reading, and rerunning reports.

**Requirements:** UX-01, UX-02, UX-03, UX-04, UX-05

**UI hint:** yes

**Success Criteria:**

1. The report workspace makes the primary next action obvious after claim extraction.
2. The user can see separate status for ingestion, ground-truth discovery, evaluation, report writing, and indexing.
3. Long-running work shows useful progress details such as provider/source names, claim counts, selected evidence counts, limits, skipped work, and current operation.
4. Fast run versus full refresh is exposed before report generation starts, with clear consequences for speed and evidence coverage.
5. Failed states identify the subsystem that failed and offer a retry, rerun, or recovery action when safe.
6. The redesigned layout is readable and stable on desktop and mobile without crowded metadata overwhelming the main report task.

**Implementation Notes:**

- The UI should make the report workflow feel like a job cockpit, not a disabled button with a spinner.
- Keep traceability visible without leading with raw UUID noise.
- Use existing component patterns where they serve the workflow, but do not preserve the current layout if it blocks clarity.

### Phase 9: v1.1 Verification and Recovery Hardening

**Status:** Planned

**Goal:** Validate async lifecycle, polling, bounded processing, retry/rerun idempotency, error mapping, and responsive UI states end to end.

**Requirements:** OPS-06

**UI hint:** yes

**Success Criteria:**

1. Backend tests cover report job start, polling, stage transitions, stored state reload, bounded processing, and retry/rerun idempotency.
2. Frontend tests or build-time checks cover loading, running, failed, retryable, succeeded, bounded, and full-refresh report states.
3. Manual verification confirms the UI no longer waits for a single long synchronous POST before showing report progress.
4. A failed provider or bounded/no-evidence run produces understandable UI copy and preserves traceable report semantics.
5. The final v1.1 verification includes the relevant backend tests and frontend production build.

**Implementation Notes:**

- Use regression tests around the exact issue: report generation should not look like a stuck request.
- Keep generated report labels and provenance traceable after bounded or reused-evidence runs.

## Requirement Coverage

| Requirement Group | Requirements | Phase |
|-------------------|--------------|-------|
| Async runtime | RPT-01, RPT-02, RPT-05, OPS-05 | Phase 6 |
| Bounded discovery and reuse | RPT-03, RPT-04, EVAL-06, SRC-06 | Phase 7 |
| Report UX | UX-01 to UX-05 | Phase 8 |
| Verification | OPS-06 | Phase 9 |

## Verification Strategy

- The async API is complete only when report generation returns a job immediately and status can be polled through completion or failure.
- Bounded UI-triggered runs must not silently weaken evidence quality; the mode and limits must be recorded in provenance.
- The UX is complete only when a user can understand the current report stage, what work is skipped or delayed, and what recovery action is available.
- The milestone is complete only when a UI-triggered report run no longer depends on one long synchronous request for ground-truth discovery and report creation.

## Next Step

Run `$gsd-discuss-phase 6` to gather implementation context for the async report job lifecycle.

---
*Roadmap created: 2026-04-18*
