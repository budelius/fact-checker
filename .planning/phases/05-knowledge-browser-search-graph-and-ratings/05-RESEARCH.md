---
phase: 05-knowledge-browser-search-graph-and-ratings
type: research
status: complete
created: 2026-04-18
requirements:
  - KB-06
  - UI-03
  - UI-04
  - UI-05
  - RAT-01
  - RAT-02
  - RAT-03
---

# Phase 5 Research

Answer: what needs to be known to plan the knowledge browser, search, graph inspection, consistency checks, and evidence-state ratings well.

## Inputs Read

- `.planning/phases/05-knowledge-browser-search-graph-and-ratings/05-CONTEXT.md`
- `.planning/phases/05-knowledge-browser-search-graph-and-ratings/05-UI-SPEC.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `docs/phase-1-contracts.md`
- `docs/phase-4-evaluation.md`
- `vault/SCHEMA.md`
- Existing backend schemas, repositories, report API, and frontend shell/components.

## Current Architecture Findings

- The core identity contract is already in place: every canonical object uses UUIDs across Markdown, MongoDB, Qdrant, and API payloads.
- `EntityType` already includes `video`, `creator`, `transcript`, `screenshot`, `claim`, `source`, `paper`, `author`, `evidence`, `report`, `rating`, and `topic`, so Phase 5 should use `rating` instead of inventing a parallel score object.
- MongoDB currently exposes `entities`, `relationships`, `ingestion_jobs`, and `pipeline_events` through `MongoRepository`; browse, graph, consistency, annotation, and rating features need read/list helpers rather than a new database layer.
- Qdrant currently has deterministic upsert behavior only. Vector-backed search needs a repository method that embeds a query, searches the existing collection, returns payloads, and supports entity-type/source/vault filters.
- `QdrantPayload` already carries the fields needed for traceability: `uuid`, `entity_type`, `vault_path`, `chunk_id`, `source`, `source_uuid`, and relationship UUIDs.
- The backend already depends on `python-frontmatter` and `pyyaml`, so vault note parsing can use the existing dependency set.
- The frontend already has the right broad layout: `AppShell`, `VaultNavigation`, `NotePreview`, `MetadataPanel`, and report components. Phase 5 should evolve these into a page-first knowledge browser instead of creating a separate app.
- Graphify is useful as product inspiration for interactive graph output, queryable graph JSON, reports, clusters, important nodes, and surprising relationships, but Phase 5 should build from MongoDB relationships and Markdown/Qdrant traceability.

## Recommended Implementation Slices

### 1. Knowledge Read Model And Browse API

Build typed backend knowledge models and an API that can list vault sections, list notes/entities by type, fetch a selected note by UUID or vault path, and return parsed frontmatter, readable Markdown body, relationships, backlinks, consistency summary, annotations, and rating summary when available.

Recommended files:

- `backend/app/schemas/knowledge.py`
- `backend/app/knowledge/vault.py`
- `backend/app/api/knowledge.py`
- `backend/app/repositories/mongo.py`
- `backend/app/main.py`
- `backend/tests/test_knowledge_api.py`
- `backend/tests/test_knowledge_vault.py`

Important planning constraints:

- Parsed frontmatter is secondary metadata. The API should provide a readable `body_markdown` separately from `frontmatter`.
- Annotation records must be separate from generated canonical notes. A small `annotations` Mongo collection or in-memory test store is acceptable, but annotation text must not be merged into canonical generated Markdown.
- Add `ratings` to browser sections only when useful, but do support `EntityType.rating` in schemas.
- Return stable display labels, UUIDs, vault paths, and entity types so the frontend never has to parse Markdown to discover identity.

### 2. Vector Search API And Command Palette Contract

Add a search path that uses the existing `OpenAIEmbeddingProvider` when an API key is configured and returns Qdrant payload matches with filters. The API should also support a deterministic fallback for tests and local development, such as title/vault path/body substring matching over parsed notes when Qdrant or embeddings are unavailable.

Recommended files:

- `backend/app/knowledge/search.py`
- `backend/app/repositories/qdrant.py`
- `backend/app/api/knowledge.py`
- `backend/tests/test_knowledge_search.py`
- `frontend/src/api/knowledge.ts`
- `frontend/src/components/CommandPalette.tsx`

Important planning constraints:

- Search result rows should include `uuid`, `entity_type`, `title`, `vault_path`, `snippet`, `score`, `source`, and optional `relationship_uuids`.
- Entity filters should support at least `paper`, `claim`, `report`, and `creator`; the frontend can expose chips or `type:paper` parsing if implementation stays small.
- Backend tests should avoid live OpenAI calls by injecting a fake embedding provider and fake Qdrant repository.
- The UI contract requires the command palette placeholder `Search the vault or jump to an entity`.

### 3. Graph Inspection And Consistency Check

Build graph inspection from MongoDB relationships, enriched with entity display labels and vault paths. Add a consistency service that compares Markdown frontmatter/body wiki links, MongoDB entity and relationship records, and Qdrant payloads.

Recommended files:

- `backend/app/knowledge/graph.py`
- `backend/app/knowledge/consistency.py`
- `backend/app/api/knowledge.py`
- `backend/tests/test_knowledge_graph.py`
- `backend/tests/test_knowledge_consistency.py`
- `frontend/src/components/KnowledgeGraphPanel.tsx`
- `frontend/src/components/ConsistencyPanel.tsx`

Important planning constraints:

- Graph JSON should be queryable and simple: `nodes`, `edges`, `selected_uuid`, optional `clusters`, `important_nodes`, and `surprises`.
- Edges should use existing relationship labels: `cites`, `supports`, `contradicts`, `authored_by`, `discussed_in`, `derived_from`, and `related_to`.
- Consistency statuses should be exactly `synced`, `drift`, and `broken` per UI-SPEC.
- Consistency detail rows should include affected UUID, entity type, store, issue, and suggested repair direction.
- Phase 5 should report drift, not silently repair stores.

### 4. Evidence-State Ratings

Create transparent rating records for creators, papers, authors, and sources based on accumulated report/evidence history. Ratings should be conservative, auditable, and explicitly experimental until there is enough history.

Recommended files:

- `backend/app/schemas/ratings.py`
- `backend/app/knowledge/ratings.py`
- `backend/app/api/knowledge.py`
- `backend/tests/test_knowledge_ratings.py`
- `vault/SCHEMA.md`
- `frontend/src/components/RatingBadge.tsx`
- `frontend/src/components/RatingBasisPanel.tsx`

Important planning constraints:

- Badge labels must be exactly `strong evidence history`, `mixed evidence history`, `limited evidence`, and `insufficient history`; early records also show `experimental`.
- Rating records must expose evidence count, label distribution, source basis, confidence level, report versions, cited evidence UUIDs, and relationship basis.
- Avoid punitive copy such as trust, reputation, reliable, unreliable, or truth score.
- Store rating records as canonical knowledge entities where possible, with generated Markdown under `vault/wiki/ratings/` and MongoDB `EntityType.rating` metadata. Update `vault/SCHEMA.md` because ratings are not currently listed as a required wiki folder.
- A derived rating algorithm can start deterministic: insufficient history for zero or too few evaluated claims, limited for small mostly one-sided history, mixed for conflicting supported/contradicted/mixed labels, and strong evidence history only when enough evaluated evidence exists and contradiction is low. The exact thresholds should be constants with tests, not hidden model output.

### 5. Frontend Knowledge Workspace

Evolve the existing three-pane shell into the Phase 5 browser.

Recommended files:

- `frontend/src/api/knowledge.ts`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/VaultNavigation.tsx`
- `frontend/src/components/NotePreview.tsx`
- `frontend/src/components/MetadataPanel.tsx`
- `frontend/src/components/CommandPalette.tsx`
- `frontend/src/components/KnowledgeGraphPanel.tsx`
- `frontend/src/components/ConsistencyPanel.tsx`
- `frontend/src/components/RatingBadge.tsx`
- `frontend/src/components/RatingBasisPanel.tsx`
- `frontend/src/data/sampleVault.ts`
- `frontend/src/styles/app.css`
- `frontend/src/styles/tokens.css`

Important planning constraints:

- The first screen is the usable knowledge vault, not a landing page.
- Keep the left rail, central readable page, and right rail. On mobile, the right rail moves below the page.
- Frontmatter must not be the main content.
- Long UUIDs, URLs, vault paths, snippets, graph node labels, and chunk IDs must wrap with `overflow-wrap: anywhere`.
- Do not introduce shadcn, Radix, Tailwind, or registry components.
- A graph library is optional. If a dependency is introduced, the plan should require explicit install, type/build verification, and a fallback relationship-list rendering for mobile.

## Validation Architecture

Phase 5 should be validated through targeted service/API/component checks and full project verification:

- Backend schema and service tests for browse, search, graph, consistency, and ratings.
- API tests for `/knowledge` endpoints using fake repositories, temporary vault files, and deterministic payloads.
- Frontend build validation with `cd frontend && yarn build`.
- Full backend test suite with `cd backend && uv run pytest -q`.
- Grep checks for forbidden rating copy: no `truth score`, `trust score`, `reputation score`, `reliable creator`, or `unreliable creator` in Phase 5 UI code.
- Requirements update only after backend tests and frontend build pass.

## Risks And Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Browser reads Markdown but ignores MongoDB/Qdrant drift | high | Add a consistency service and UI panel in the same phase, with explicit `synced`, `drift`, and `broken` states. |
| Search becomes a fake frontend-only filter | high | Add backend Qdrant search method and inject fake vector providers only in tests. |
| Ratings become hidden reputation scores | high | Use evidence-state badge labels and expose evidence count, label distribution, source basis, and confidence level. |
| Annotations corrupt generated provenance | high | Store annotations separately from canonical generated note body/frontmatter. |
| Graph becomes decorative | medium | Require selectable nodes/edges, relationship details, and source/vault provenance. |
| Phase scope becomes too large for one execution wave | medium | Plan backend read/search/graph/rating slices first, then frontend integration, then docs/final verification. |

## Planning Recommendation

Use six plans:

1. Backend knowledge read models, browse API, and annotations.
2. Backend vector search and command-palette search API.
3. Backend graph inspection and consistency check.
4. Backend evidence-state ratings and rating Markdown records.
5. Frontend knowledge workspace: page browser, command palette, graph, consistency, annotations, and rating badges.
6. Documentation, AGENTS update, requirements/roadmap/state tracking, and final verification.

The first four backend plans can partially parallelize after the shared schemas/API route contract is established. The frontend plan should depend on backend response shapes. The final documentation and tracking plan should depend on all implementation plans.

## RESEARCH COMPLETE
