---
phase: 05-knowledge-browser-search-graph-and-ratings
plan: "04"
subsystem: backend evidence-state ratings
tags: [knowledge, ratings, markdown]
key-files:
  created:
    - backend/app/schemas/ratings.py
    - backend/app/knowledge/ratings.py
    - backend/tests/test_knowledge_ratings.py
  modified:
    - backend/app/api/knowledge_ratings.py
    - vault/SCHEMA.md
requirements-completed: [RAT-01, RAT-02, RAT-03]
completed: 2026-04-18
---

# Phase 05 Plan 04: Evidence-State Ratings Summary

Transparent evidence-state rating records are implemented for creators, papers, authors, and sources with generated Markdown under `vault/wiki/ratings/`.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1-3 | cd16de7 | Added rating schemas, deterministic rating service, Markdown writer, API routes, and copy-safety tests. |

## Verification

- `cd backend && uv run pytest tests/test_knowledge_ratings.py tests/test_knowledge_api.py -q` passed.
- Required grep checks for approved badge copy, experimental marker, `EntityType.rating`, `vault/wiki/ratings`, and absent forbidden rating copy passed.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

Ratings expose evidence count, label distribution, source basis, confidence level, report versions, evidence UUIDs, and relationship UUIDs while staying conservative for early evidence history.
