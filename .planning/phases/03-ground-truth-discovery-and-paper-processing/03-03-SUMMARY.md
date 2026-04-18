---
phase: 03-ground-truth-discovery-and-paper-processing
plan: "03"
subsystem: backend-discovery-policy
tags: [ground-truth, dedupe, source-selection, provenance, no-paper]
requires:
  - phase: 03-ground-truth-discovery-and-paper-processing
    provides: 03-01 schemas and 03-02 provider candidates
provides:
  - Candidate merge keys and dedupe policy
  - Paper/preprint-only ground-truth selection policy
  - Discovery orchestration with source-discovery trace events
affects: [phase-3-pipeline, phase-4-evaluation]
tech-stack:
  added: []
  patterns: [identifier-first merge keys, supplemental non-paper decisions, explicit no-paper reason]
key-files:
  created:
    - backend/app/ground_truth/dedupe.py
    - backend/app/ground_truth/selection.py
    - backend/app/ground_truth/progress.py
    - backend/app/ground_truth/discovery.py
    - backend/tests/test_ground_truth_discovery.py
  modified: []
key-decisions:
  - "Merge candidates by DOI, arXiv, OpenAlex, Semantic Scholar, normalized URL, then title/authors fallback."
  - "Only paper and preprint candidates above threshold with stable provenance can be selected as ground truth."
  - "No selected paper/preprint appends `no_scientific_evidence_found_for_now` without claiming no paper exists anywhere."
patterns-established:
  - "Discovery service emits the fixed source-discovery stages used by progress UI and trace logs."
  - "Selection records a SourceDecision for selected, rejected, supplemental, and no-paper cases."
requirements-completed:
  - SRC-01
  - SRC-02
  - SRC-03
  - SRC-04
  - SRC-05
duration: 18 min
completed: 2026-04-18
---

# Phase 3 Plan 03: Discovery Policy Summary

**Candidate dedupe, paper-only source selection, no-paper policy, and source-discovery trace orchestration**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-18T13:38:00Z
- **Completed:** 2026-04-18T13:56:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added merge logic that preserves external IDs, authors, discovery paths, raw provenance, URLs, and confidence.
- Added strict selection policy that marks non-paper sources as supplemental and appends the required no-paper decision when no paper/preprint is selected.
- Added `GroundTruthDiscoveryService` to load Phase 2 payloads, run provider clients, merge candidates, select sources, and emit trace events.

## Task Commits

1. **Tasks 1-3: Add dedupe, selection, and discovery orchestration** - `f7c84b5`

## Files Created/Modified

- `backend/app/ground_truth/dedupe.py` - Candidate merge-key and merge logic.
- `backend/app/ground_truth/selection.py` - Ground-truth selection and no-paper policy.
- `backend/app/ground_truth/progress.py` - Source-discovery trace event builder.
- `backend/app/ground_truth/discovery.py` - Discovery orchestration service.
- `backend/tests/test_ground_truth_discovery.py` - Dedupe, selection, trace, and no-paper tests.

## Decisions Made

- Kept candidate selection separate from provider clients so search results cannot self-certify as ground truth.
- Treated web non-paper sources as useful supplemental trace material, never selected evidence.
- Used the exact machine reason `no_scientific_evidence_found_for_now` and user-facing operation `No scientific evidence found for now.`

## Deviations from Plan

Implemented inline as a single commit because MCP-backed worker execution was disabled by user request. Scope and tests match the plan.

**Total deviations:** 1 execution-mode deviation.
**Impact on plan:** None.

## Issues Encountered

None in the inline implementation.

## Verification

- `uv run pytest tests/test_ground_truth_discovery.py -q` passed: 8 tests.
- Wave 3 combined gate passed with discovery, persistence, and indexing tests: 16 tests.

## User Setup Required

None.

## Next Phase Readiness

Plan 06 can run the discovery service from an ingestion payload and pass selected paper decisions into processing/persistence/indexing.

## Self-Check: PASSED

---
*Phase: 03-ground-truth-discovery-and-paper-processing*
*Completed: 2026-04-18*
