---
phase: 03-ground-truth-discovery-and-paper-processing
plan: "05"
subsystem: backend-paper-knowledge
tags: [markdown, mongodb, qdrant, embeddings, summarization, vault]
requires:
  - phase: 03-ground-truth-discovery-and-paper-processing
    provides: 03-01 paper schemas and 03-04 parsed chunks
provides:
  - Obsidian-compatible paper Markdown notes
  - Structured paper summarization prompt, parser, and deterministic fallback
  - MongoDB-compatible paper, author, evidence entities and relationships
  - Qdrant payload indexing for paper chunks and summaries
affects: [phase-3-pipeline, phase-4-evidence-evaluation, phase-5-browser-search-graph]
tech-stack:
  added: []
  patterns: [single-source paper records, untrusted paper prompt wrapping, fake embedding tests]
key-files:
  created:
    - backend/app/ground_truth/markdown.py
    - backend/app/ground_truth/summarization.py
    - backend/app/ground_truth/persistence.py
    - backend/app/ground_truth/indexing.py
    - backend/tests/test_ground_truth_persistence.py
    - backend/tests/test_ground_truth_indexing.py
  modified: []
key-decisions:
  - "Markdown paper notes are generated from the same PaperMetadata/PaperSummary/SourceDecision records persisted to stores."
  - "Fallback summaries derive UUIDs from the paper UUID so local runs are deterministic."
  - "Qdrant collection size is inferred from the first embedding vector instead of hard-coded."
patterns-established:
  - "Paper chunks index as evidence payloads; paper summaries index as paper payloads with chunk_id `summary`."
  - "Persistence writes paper, author, evidence, authored_by, derived_from, and cites records with vault path traceability."
requirements-completed:
  - SRC-04
  - PPR-01
  - PPR-04
  - PPR-05
duration: 17 min
completed: 2026-04-18
---

# Phase 3 Plan 05: Paper Knowledge Summary

**Markdown paper notes, structured summaries, MongoDB-compatible entities, and Qdrant payloads for chunks and summaries**

## Performance

- **Duration:** 17 min
- **Started:** 2026-04-18T13:56:00Z
- **Completed:** 2026-04-18T14:13:00Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Added paper Markdown generation with required frontmatter, source links, abstract, methods, key claims, limitations, references, and provenance.
- Added untrusted-wrapped summarization prompts, strict JSON parsing, and deterministic fallback summary generation.
- Added vault/MongoDB persistence and Qdrant indexing for paper chunks and summary records.

## Task Commits

1. **Tasks 1-4: Add Markdown, summarization, persistence, and indexing** - `256df0f`

## Files Created/Modified

- `backend/app/ground_truth/markdown.py` - Paper note builder.
- `backend/app/ground_truth/summarization.py` - Prompt builder, parser, fallback, and OpenAI wrapper.
- `backend/app/ground_truth/persistence.py` - Vault and MongoDB-compatible persistence.
- `backend/app/ground_truth/indexing.py` - Embedding provider and Qdrant indexing functions.
- `backend/tests/test_ground_truth_persistence.py` - Markdown, summary, persistence tests.
- `backend/tests/test_ground_truth_indexing.py` - Fake-vector indexing tests.

## Decisions Made

- Used deterministic UUIDs for fallback summaries and persistence relationships where possible.
- Kept live OpenAI embedding/summarization behind injectable providers so tests stay offline.
- Stored Markdown under `vault/wiki/papers/` and indexed payloads with vault path/source UUID trace fields.

## Deviations from Plan

Implemented inline as a single commit because MCP-backed worker execution was disabled by user request. Scope and tests match the plan.

**Total deviations:** 1 execution-mode deviation.
**Impact on plan:** None.

## Issues Encountered

- Initial fallback summary test revealed random summary UUIDs; fixed by deriving fallback summary UUIDs from the paper UUID.

## Verification

- `uv run pytest tests/test_ground_truth_persistence.py tests/test_ground_truth_indexing.py -q` passed: 8 tests.
- Wave 3 combined gate passed with discovery, persistence, and indexing tests: 16 tests.

## User Setup Required

None for local tests. Live summarization/indexing requires `OPENAI_API_KEY`.

## Next Phase Readiness

Plan 06 can compose discovery, paper processing, Markdown/MongoDB persistence, and Qdrant indexing into one API-triggered workflow.

## Self-Check: PASSED

---
*Phase: 03-ground-truth-discovery-and-paper-processing*
*Completed: 2026-04-18*
