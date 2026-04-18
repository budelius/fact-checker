# Phase 5 Knowledge Browser

## Scope

Phase 5 makes the owned Markdown, MongoDB, and Qdrant knowledge useful through browsing, search, graph inspection, consistency checks, annotations, and evidence-state ratings.

The user-facing product surface is a page-first knowledge vault. Markdown remains the canonical human-readable store, MongoDB remains the structured entity and relationship store, and Qdrant remains the vector payload store for retrieval.

Graphify-inspired product ideas shaped the graph view: queryable graph data, important nodes, clusters, and relationship explanations. The runtime source of truth is still this app's MongoDB relationships plus Markdown and Qdrant traceability.

## API Routes

Browse routes:

- `GET /knowledge/sections` returns vault sections and counts.
- `GET /knowledge/notes` returns note list items, optionally filtered by `entity_type`.
- `GET /knowledge/notes/{note_uuid}` returns a parsed note with `frontmatter`, readable `body_markdown`, backlinks, relationship rows, annotations, and optional rating/consistency summaries.
- `POST /knowledge/notes/{note_uuid}/annotations` creates a user annotation record.

Search routes:

- `GET /knowledge/search` accepts `q`, repeated `entity_type`, and `limit`.
- Results include UUID, entity type, title, vault path, snippet, score, source, chunk ID, source UUID, and relationship UUIDs.
- Search uses Qdrant when embeddings and Qdrant are available. Without that runtime support it falls back to deterministic local vault text matching.

Graph and consistency routes:

- `GET /knowledge/graph/{entity_uuid}` returns nodes, edges, important nodes, and clusters built from stored relationships.
- `GET /knowledge/consistency` compares Markdown notes, MongoDB entities/relationships, and Qdrant payloads.
- Consistency issues use only `synced`, `drift`, and `broken`. The service reports suggested repair direction and does not auto-repair stores.

Rating routes:

- `GET /knowledge/ratings/{target_uuid}` returns the latest evidence-state rating record when present.
- `POST /knowledge/ratings/{target_uuid}/refresh` derives a rating for a creator, paper, author, or source, writes generated Markdown under `vault/wiki/ratings/`, upserts a rating entity, and returns the record.

## Annotation Boundary

User annotations are separate records. They are displayed next to generated notes but annotations are separate from canonical generated Markdown and do not rewrite note body text or frontmatter.

Annotation text is user content. It is not source evidence unless a later source-policy phase explicitly promotes it.

## Search Policy

Qdrant search is the primary search path when a configured embedding provider and Qdrant collection are available. The payload contract preserves traceability to `uuid`, `entity_type`, `vault_path`, `source`, `chunk_id`, `source_uuid`, and relationship UUIDs.

The fallback path exists for local development and tests. It searches parsed vault note title, path, and body text and marks results as not vector-backed.

## Graph Policy

Graph inspection is functional and explanatory. The graph response is derived from `KnowledgeEntity` and `KnowledgeRelationship` records and exposes readable titles, UUIDs, relationship types, provenance, node degree, important nodes, and entity-type clusters.

The graph view is a second signal for context, not a verdict engine. It explains relationship trails around claims, papers, authors, creators, sources, evidence, and reports.

## Consistency Policy

Consistency checks compare:

- Markdown note UUIDs and vault paths.
- MongoDB entity and relationship records.
- Qdrant payload UUIDs and vault paths.

The endpoint reports missing MongoDB records, missing Qdrant payloads, broken relationships, and orphan vectors. It does not mutate Markdown, MongoDB, or Qdrant.

## Evidence-State Ratings

Ratings describe accumulated evidence state. They are not hidden rankings.

Approved badge copy:

- `strong evidence history`
- `mixed evidence history`
- `limited evidence`
- `insufficient history`

Each rating exposes evidence count, label distribution, source basis, confidence level, report version UUIDs, evidence UUIDs, relationship UUIDs, generated timestamp, and vault path. Ratings are experimental until `evidence_count >= 10`.

## Frontend Workspace

The React workspace opens directly to the knowledge vault. It includes:

- Left rail vault sections, including ratings.
- Central readable note page with generated Markdown body before frontmatter.
- Command palette search with `Search the vault or jump to an entity`.
- Graph and consistency panels that explain relationships and drift.
- Right rail metadata, annotations, consistency status, graph counts, and rating basis.
- Responsive layout that moves the right rail below the page on narrow screens.

## Verification

```bash
cd backend && uv run pytest tests/test_knowledge_vault.py tests/test_knowledge_api.py tests/test_knowledge_search.py tests/test_knowledge_graph.py tests/test_knowledge_consistency.py tests/test_knowledge_ratings.py -q
cd backend && uv run pytest -q
cd frontend && yarn build
run the Phase 5 copy-safety grep over backend, frontend, and this document
```
