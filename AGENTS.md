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

Phase 5: Knowledge Browser, Search, Graph, and Ratings is implemented.

Goal: make accumulated Markdown/vector/graph knowledge useful through browsing, search, graph inspection, consistency checks, and transparent ratings.

## Important Constraints

- Markdown is the canonical human-readable knowledge store.
- MongoDB is the structured metadata and graph relationship store.
- Qdrant is the vector database target.
- OpenAI APIs are allowed for v1, but durable knowledge must remain outside OpenAI-hosted memory.
- v1 input includes public TikTok links, pasted transcript fixtures, and user-owned video uploads stored locally under `vault/raw/videos/`.
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

## Phase 2 Contract Files

- `docs/phase-2-ingestion.md`
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md`
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-UI-SPEC.md`
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-RESEARCH.md`
- `backend/app/schemas/ingestion.py`
- `backend/app/api/ingestion.py`

## Phase 3 Contract Files

- `docs/phase-3-ground-truth.md`
- `.planning/phases/03-ground-truth-discovery-and-paper-processing/03-CONTEXT.md`
- `.planning/phases/03-ground-truth-discovery-and-paper-processing/03-RESEARCH.md`
- `backend/app/schemas/ground_truth.py`
- `backend/app/api/ground_truth.py`
- `backend/app/ground_truth/discovery.py`
- `backend/app/ground_truth/pipeline.py`
- `backend/app/ground_truth/persistence.py`
- `backend/app/ground_truth/indexing.py`

## Phase 4 Contract Files

- `docs/phase-4-evaluation.md`
- `.planning/phases/04-evidence-evaluation-and-fact-check-reports/04-CONTEXT.md`
- `.planning/phases/04-evidence-evaluation-and-fact-check-reports/04-UI-SPEC.md`
- `.planning/phases/04-evidence-evaluation-and-fact-check-reports/04-RESEARCH.md`
- `backend/app/schemas/evaluation.py`
- `backend/app/api/reports.py`
- `backend/app/evaluation/evidence.py`
- `backend/app/evaluation/evaluator.py`
- `backend/app/evaluation/validation.py`
- `backend/app/evaluation/markdown.py`
- `backend/app/evaluation/persistence.py`
- `backend/app/evaluation/pipeline.py`
- `vault/templates/report.md`
- `frontend/src/api/reports.ts`
- `frontend/src/components/reports/`

## Phase 5 Contract Files

- `docs/phase-5-knowledge-browser.md`
- `.planning/phases/05-knowledge-browser-search-graph-and-ratings/05-CONTEXT.md`
- `.planning/phases/05-knowledge-browser-search-graph-and-ratings/05-UI-SPEC.md`
- `.planning/phases/05-knowledge-browser-search-graph-and-ratings/05-RESEARCH.md`
- `backend/app/schemas/knowledge.py`
- `backend/app/schemas/ratings.py`
- `backend/app/api/knowledge.py`
- `backend/app/api/knowledge_browse.py`
- `backend/app/api/knowledge_search.py`
- `backend/app/api/knowledge_graph.py`
- `backend/app/api/knowledge_ratings.py`
- `backend/app/knowledge/vault.py`
- `backend/app/knowledge/annotations.py`
- `backend/app/knowledge/search.py`
- `backend/app/knowledge/graph.py`
- `backend/app/knowledge/consistency.py`
- `backend/app/knowledge/ratings.py`
- `frontend/src/api/knowledge.ts`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/CommandPalette.tsx`
- `frontend/src/components/KnowledgeGraphPanel.tsx`
- `frontend/src/components/ConsistencyPanel.tsx`
- `frontend/src/components/RatingBadge.tsx`
- `frontend/src/components/RatingBasisPanel.tsx`
- `backend/tests/test_knowledge_vault.py`
- `backend/tests/test_knowledge_api.py`
- `backend/tests/test_knowledge_search.py`
- `backend/tests/test_knowledge_graph.py`
- `backend/tests/test_knowledge_consistency.py`
- `backend/tests/test_knowledge_ratings.py`

## Next Step

Run:

`$gsd-complete-milestone`

For a final user acceptance pass before archiving the milestone, run:

`$gsd-verify-work`
