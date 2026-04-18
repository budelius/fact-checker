# AGENTS.md

## Project

Fact Checker is a user-owned AI research fact-checking system. The first milestone takes a public TikTok video link, extracts claims, finds relevant papers or preprints, evaluates claims against evidence, and stores the result in an owned Markdown knowledge base with vector and graph indexes.

## Core Value

Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## GSD Workflow

- Project context: `.planning/PROJECT.md`
- Requirements: `.planning/REQUIREMENTS.md`
- Roadmap: `.planning/ROADMAP.md`
- Current state: `.planning/STATE.md`
- Research notes: `.planning/research/`

Before planning or implementing a phase, read the project context, requirements, roadmap, and state. Keep changes aligned to the current phase unless the user explicitly changes scope.

## Current Focus

Phase 1: Foundation and Knowledge Store Contracts.

Goal: establish the app skeleton, storage contracts, provider boundaries, and owned knowledge model that every later phase writes into.

## Important Constraints

- Markdown is the canonical human-readable knowledge store.
- MongoDB is the structured metadata and graph relationship store.
- Qdrant is the vector database target.
- OpenAI APIs are allowed for v1, but durable knowledge must remain outside OpenAI-hosted memory.
- v1 input is public TikTok links only.
- v1 ground truth is papers and preprints only.
- Fact-check labels are supported, contradicted, mixed, or insufficient evidence.
- Every label, rating, and report must be traceable to underlying evidence.
- TikTok ingestion must stay behind a compliance-gated adapter.

## Phase 1 Contract Files

- `docs/phase-1-contracts.md`
- `vault/SCHEMA.md`
- `backend/app/schemas/entities.py`
- `backend/app/schemas/relationships.py`
- `backend/app/schemas/vector_payloads.py`
- `backend/app/contracts/store_sync.py`

## Next Step

Run:

`$gsd-discuss-phase 1`

For frontend interaction design before planning, run:

`$gsd-ui-phase 1`
