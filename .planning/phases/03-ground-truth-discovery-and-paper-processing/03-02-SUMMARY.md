---
phase: 03-ground-truth-discovery-and-paper-processing
plan: "02"
subsystem: backend-provider-clients
tags: [ground-truth, openai-web-search, arxiv, openalex, semantic-scholar, fixtures]
requires:
  - phase: 03-ground-truth-discovery-and-paper-processing
    provides: 03-01 schemas, settings, and logging contracts
provides:
  - DiscoveryQuery generation from claims, research-basis hints, and screenshot clues
  - arXiv, OpenAlex, Semantic Scholar, and OpenAI web-search candidate normalization
  - Deterministic provider fixtures for no-network tests
affects: [phase-3-discovery, phase-3-selection, phase-3-e2e]
tech-stack:
  added: []
  patterns: [provider fixture parsers, normalized PaperCandidate outputs, citation/source provenance]
key-files:
  created:
    - backend/app/ground_truth/__init__.py
    - backend/app/ground_truth/queries.py
    - backend/app/ground_truth/clients/arxiv.py
    - backend/app/ground_truth/clients/openalex.py
    - backend/app/ground_truth/clients/semantic_scholar.py
    - backend/app/ground_truth/clients/openai_search.py
    - backend/tests/fixtures/ground_truth/arxiv_attention.xml
    - backend/tests/fixtures/ground_truth/openai_web_search_attention.json
    - backend/tests/fixtures/ground_truth/openalex_attention.json
    - backend/tests/fixtures/ground_truth/semantic_scholar_attention.json
  modified:
    - backend/tests/test_ground_truth_clients.py
key-decisions:
  - "Provider clients return PaperCandidate records only; selection remains a later policy step."
  - "OpenAI web-search preserves both url_citation annotations and web_search_call.action.sources."
  - "Non-paper web sources normalize as supplemental candidates, not ground truth."
patterns-established:
  - "Each provider has a pure fixture parser used by unit tests and a thin live client wrapper."
  - "DiscoveryQuery records query text, source candidate UUID, claim UUID, provider hint, and reasons."
requirements-completed:
  - SRC-01
  - SRC-02
  - SRC-04
  - SRC-05
duration: 18 min
completed: 2026-04-18
---

# Phase 3 Plan 02: Provider Clients Summary

**Paper discovery query generation with arXiv, OpenAlex, Semantic Scholar, and OpenAI web-search candidate adapters**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-18T13:20:01Z
- **Completed:** 2026-04-18T13:38:00Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Added deterministic query generation from exact identifiers, title hints, claims, transcript excerpts, and screenshot clue text.
- Added provider clients and pure parsers for arXiv Atom XML, OpenAlex Works JSON, Semantic Scholar paper JSON, and OpenAI Responses web-search output.
- Added fixtures and tests proving citations, sources, paper/non-paper classification, and API-key redaction behavior.

## Task Commits

1. **Task 1: Add discovery query generation from Phase 2 context** - `66d22b4`
2. **Tasks 2-3: Add paper index and OpenAI web search clients** - `63c53fc`

## Files Created/Modified

- `backend/app/ground_truth/queries.py` - Builds deduped discovery queries with trace reasons.
- `backend/app/ground_truth/clients/arxiv.py` - arXiv search client and Atom parser.
- `backend/app/ground_truth/clients/openalex.py` - OpenAlex Works search client and parser.
- `backend/app/ground_truth/clients/semantic_scholar.py` - Semantic Scholar search client and parser.
- `backend/app/ground_truth/clients/openai_search.py` - OpenAI web-search client and response parser.
- `backend/tests/test_ground_truth_clients.py` - Provider fixture and query tests.
- `backend/tests/fixtures/ground_truth/*` - Deterministic provider fixtures.

## Decisions Made

- Kept provider clients synchronous and small so orchestration can own retry/rate-limit policy later.
- Stored raw provider snippets with secret redaction instead of copying whole client config or API keys.
- Classified non-paper web URLs as supplemental at normalization time while still preserving their source traces.

## Deviations from Plan

The closed worker committed query generation before the run was switched to inline execution. The remaining provider-client tasks were completed inline. This did not change scope or behavior.

**Total deviations:** 1 execution-mode deviation.
**Impact on plan:** None; all Plan 02 acceptance criteria pass.

## Issues Encountered

MCP-backed workers stalled, so execution was switched to inline shell/file edits per the user's instruction.

## Verification

- `uv run pytest tests/test_ground_truth_clients.py -q` passed: 8 tests.
- `git diff --check` passed for Plan 02 files.

## User Setup Required

None for fixture tests. Live use later requires `OPENAI_API_KEY`; `OPENALEX_EMAIL` and `SEMANTIC_SCHOLAR_API_KEY` remain optional settings.

## Next Phase Readiness

Plan 03 can merge and select candidates from normalized provider outputs without calling provider-specific APIs directly.

## Self-Check: PASSED

---
*Phase: 03-ground-truth-discovery-and-paper-processing*
*Completed: 2026-04-18*
