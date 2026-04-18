---
phase: 02-tiktok-ingestion-and-claim-extraction
plan: "03"
subsystem: backend
tags: [claims, triage, pydantic, prompt-safety, research-basis]
requires:
  - phase: 02-tiktok-ingestion-and-claim-extraction
    provides: Plan 01 schemas and Plan 02 transcript/keyframe artifacts
provides:
  - Claim extraction provider boundary and parse result model
  - Untrusted transcript/visual prompt construction
  - Deterministic DOI, arXiv, URL, and paper-reference triage
affects: [phase-2-api, phase-3-source-discovery, phase-4-evaluation]
tech-stack:
  added: []
  patterns: [untrusted input wrapping, parse-failure state, source-candidate-only triage]
key-files:
  created:
    - backend/app/ingestion/claims.py
    - backend/app/ingestion/research_basis.py
    - backend/tests/test_claim_extraction.py
    - backend/tests/test_research_basis.py
  modified:
    - backend/app/schemas/ingestion.py
key-decisions:
  - "Claim extraction returns failed parse state instead of partial claims on malformed provider output."
  - "Research-basis triage stores candidates only and does not call source discovery providers."
  - "ResearchBasisCandidate now carries optional source_uuid for transcript/screenshot traceability."
patterns-established:
  - "All external transcript and visual text is wrapped with wrap_untrusted_text before provider use."
  - "Triage classifies source candidates, opinion/unratable, no source, and manual review without evidence labels."
requirements-completed: [CLM-01, CLM-02, CLM-03, ING-04, ING-05]
duration: 9min
completed: 2026-04-18
---

# Phase 2 Plan 03 Summary

**Schema-validated claim extraction and deterministic research-basis triage without paper discovery**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-18T12:02:00Z
- **Completed:** 2026-04-18T12:10:56Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `ClaimExtractionProvider`, `ClaimExtractionResult`, prompt construction, and JSON parsing into validated `ExtractedClaim` objects.
- Added explicit failed parse handling for invalid provider output.
- Added deterministic research-basis candidate extraction and triage states for source candidates, opinion/unratable, no source, and manual review.

## Task Commits

1. **Task 1: Add claim extraction provider boundary and parser** - included in plan commit.
2. **Task 2: Add deterministic research-basis triage** - included in plan commit.

## Files Created/Modified

- `backend/app/ingestion/claims.py` - Provider protocol, untrusted prompt builder, and schema parser.
- `backend/app/ingestion/research_basis.py` - DOI/arXiv/URL/reference candidate extraction and triage.
- `backend/tests/test_claim_extraction.py` - Prompt wrapping, valid parse, and invalid parse tests.
- `backend/tests/test_research_basis.py` - Candidate and triage state tests.
- `backend/app/schemas/ingestion.py` - Added optional `source_uuid` to research-basis candidates.

## Decisions Made

- Used deterministic regex triage only; no paper APIs, search calls, downloads, or evaluation in Phase 2.
- Treated source-clue screenshots without readable text as `needs_manual_review`.
- Kept all extracted claims at `evidence_status: pending`.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope creep.

## Issues Encountered

None.

## Verification

- `cd backend && uv run pytest tests/test_claim_extraction.py tests/test_research_basis.py -q` -> 7 passed.
- `grep -q "wrap_untrusted_text" backend/app/ingestion/claims.py` -> passed.
- `grep -q "claim_extraction_parse_failed" backend/app/ingestion/claims.py` -> passed.
- `grep -q "opinion_or_unratable" backend/app/ingestion/research_basis.py` -> passed.
- `! grep -q "Semantic Scholar" backend/app/ingestion/research_basis.py` -> passed.

## User Setup Required

None - no provider credentials are required for deterministic triage or parse tests.

## Next Phase Readiness

Plan 04 can orchestrate pasted transcript and uploaded video jobs through transcript artifact construction, provider-disabled claim extraction, and research-basis triage.

---
*Phase: 02-tiktok-ingestion-and-claim-extraction*
*Completed: 2026-04-18*
