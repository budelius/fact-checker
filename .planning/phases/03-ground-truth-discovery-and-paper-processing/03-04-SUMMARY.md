---
phase: 03-ground-truth-discovery-and-paper-processing
plan: "04"
subsystem: backend-paper-processing
tags: [ground-truth, pdf, pypdf, vault, chunking]
requires:
  - phase: 03-ground-truth-discovery-and-paper-processing
    provides: 03-01 schemas, settings, and vault contracts
provides:
  - Lawful public PDF acquisition policy and raw vault writer
  - pypdf parsing with explicit parsed, metadata_only, and failed states
  - Deterministic paper chunking with trace fields
affects: [phase-3-persistence, phase-3-indexing, phase-3-pipeline]
tech-stack:
  added: []
  patterns: [public PDF guardrails, metadata-only fallback, deterministic chunk IDs]
key-files:
  created:
    - backend/app/ground_truth/acquisition.py
    - backend/app/ground_truth/parsing.py
    - backend/app/ground_truth/chunking.py
    - backend/tests/test_paper_processing.py
    - backend/tests/fixtures/ground_truth/sample-paper.pdf
  modified: []
key-decisions:
  - "Only public PDF-like URLs without credentials or private host targets are eligible for download."
  - "Unavailable, oversized, non-PDF, or image-only papers become metadata_only instead of failed truth claims."
  - "Chunk IDs are deterministic by page start and sequence index."
patterns-established:
  - "Paper acquisition writes `vault/raw/papers/{slug}.pdf` only after content-type/size/public checks."
  - "Parsing and chunking preserve paper UUID, source UUID, vault path, source URL, and page range."
requirements-completed:
  - PPR-02
  - PPR-03
duration: 14 min
completed: 2026-04-18
---

# Phase 3 Plan 04: Paper Processing Summary

**Lawful PDF acquisition, text parsing, and deterministic paper chunks with traceable vault/source metadata**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-18T13:24:00Z
- **Completed:** 2026-04-18T13:38:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added PDF acquisition guardrails for disabled downloads, missing public PDF URLs, oversized files, non-PDF responses, private URLs, and successful raw vault writes.
- Added pypdf parsing that returns explicit `parsed`, `metadata_only`, or `failed` states.
- Added chunking that creates deterministic chunk IDs and preserves paper/source/vault/page trace fields.

## Task Commits

1. **Tasks 1-3: Add paper acquisition, parsing, and chunking** - `3af17cb`

## Files Created/Modified

- `backend/app/ground_truth/acquisition.py` - Public PDF download policy and raw vault writes.
- `backend/app/ground_truth/parsing.py` - pypdf page text extraction and fallback states.
- `backend/app/ground_truth/chunking.py` - Deterministic chunk generation.
- `backend/tests/test_paper_processing.py` - Acquisition, parsing, and chunking tests.
- `backend/tests/fixtures/ground_truth/sample-paper.pdf` - Tiny deterministic PDF fixture.

## Decisions Made

- Returned `metadata_only` for blocked or unavailable downloads to preserve traceability without overclaiming.
- Rejected private/localhost/non-global IP PDF targets before any HTTP fetch.
- Kept chunking page-scoped for MVP; later section detection can add richer labels without changing chunk identity.

## Deviations from Plan

The closed worker left a complete Plan 04 draft in the workspace before shutdown. It was inspected, verified, and committed inline as one implementation commit instead of three task commits.

**Total deviations:** 1 execution-mode deviation.
**Impact on plan:** None; all Plan 04 acceptance criteria pass.

## Issues Encountered

MCP-backed workers stalled, so execution was switched to inline shell/file edits per the user's instruction.

## Verification

- `uv run pytest tests/test_paper_processing.py -q` passed: 10 tests.
- `git diff --check` passed for Plan 04 files.

## User Setup Required

None.

## Next Phase Readiness

Plan 05 can persist paper metadata, summaries, chunks, and Qdrant payloads using stable acquisition/parsing/chunk contracts.

## Self-Check: PASSED

---
*Phase: 03-ground-truth-discovery-and-paper-processing*
*Completed: 2026-04-18*
