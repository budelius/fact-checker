---
phase: 05-knowledge-browser-search-graph-and-ratings
type: patterns
status: complete
created: 2026-04-18
---

# Phase 5 Pattern Map

This map connects planned Phase 5 files to existing local analogs so execution can follow current project style.

## Backend API Patterns

| Planned file | Role | Closest analog | Pattern to reuse |
|--------------|------|----------------|------------------|
| `backend/app/api/knowledge.py` | `/knowledge` router aggregation | `backend/app/main.py`, `backend/app/api/reports.py` | Import typed routers and expose deterministic JSON payloads through FastAPI. |
| `backend/app/api/knowledge_browse.py` | Browse/list/fetch routes | `backend/app/api/reports.py`, `backend/app/api/ground_truth.py` | Use `APIRouter`, dependency injection helpers, `HTTPException` for missing UUIDs, and Pydantic response serialization. |
| `backend/app/api/knowledge_search.py` | Search routes | `backend/app/api/ground_truth.py` | Keep provider dependencies injectable so tests avoid live OpenAI/Qdrant calls. |
| `backend/app/api/knowledge_graph.py` | Graph and consistency routes | `backend/app/api/reports.py` | Return complete typed payloads; avoid frontend-only derivation. |
| `backend/app/api/knowledge_ratings.py` | Rating routes | `backend/app/api/reports.py` | Store/fetch derived objects through deterministic service functions and expose 404s for missing source records. |

## Backend Service Patterns

| Planned file | Role | Closest analog | Pattern to reuse |
|--------------|------|----------------|------------------|
| `backend/app/knowledge/vault.py` | Parse Markdown vault notes | `backend/app/ground_truth/markdown.py`, `backend/app/evaluation/markdown.py` | Keep Markdown rendering/writing deterministic and test with temporary vault files. |
| `backend/app/knowledge/search.py` | Embed query and search Qdrant | `backend/app/ground_truth/indexing.py` | Reuse `OpenAIEmbeddingProvider` injection and fake providers in tests. |
| `backend/app/knowledge/graph.py` | Relationship graph read model | `backend/app/evaluation/pipeline.py` relationship writes | Build from `KnowledgeRelationship` and `KnowledgeEntity`, not frontend fixtures. |
| `backend/app/knowledge/consistency.py` | Markdown/Mongo/Qdrant drift checks | `backend/app/ground_truth/indexing.py`, `vault/SCHEMA.md` | Compare UUIDs, vault paths, relationship UUIDs, and Qdrant payloads explicitly. |
| `backend/app/knowledge/ratings.py` | Derived evidence-state rating records | `backend/app/evaluation/evaluator.py`, `backend/app/evaluation/pipeline.py` | Keep deterministic logic testable and separate from LLM output. |

## Schema Patterns

| Planned file | Role | Closest analog | Pattern to reuse |
|--------------|------|----------------|------------------|
| `backend/app/schemas/knowledge.py` | Browse/search/graph/consistency API models | `backend/app/schemas/evaluation.py`, `backend/app/schemas/ground_truth.py` | Pydantic models with UUID fields, enum literals, defaults, and JSON-safe structures. |
| `backend/app/schemas/ratings.py` | Rating labels and basis | `backend/app/schemas/evaluation.py` | Enumerate allowed labels and validate derived payload shape. |

## Repository Patterns

| Planned file | Role | Closest analog | Pattern to reuse |
|--------------|------|----------------|------------------|
| `backend/app/repositories/mongo.py` | Entity/relationship/annotation listing | Existing `upsert_entity`, `upsert_relationship`, `get_entity` | Add narrow read helpers without replacing the repository. |
| `backend/app/repositories/qdrant.py` | Search and payload scroll | Existing `ensure_collection`, `upsert_payload` | Keep deterministic point ID behavior and return JSON payload dicts to services. |

## Frontend Patterns

| Planned file | Role | Closest analog | Pattern to reuse |
|--------------|------|----------------|------------------|
| `frontend/src/api/knowledge.ts` | Knowledge API client | `frontend/src/api/reports.ts`, `frontend/src/api/groundTruth.ts` | Use typed fetch helpers and shared API base handling. |
| `frontend/src/components/AppShell.tsx` | Browser shell composition | Existing `AppShell.tsx` | Preserve topbar, left rail, main pane, and right rail. |
| `frontend/src/components/VaultNavigation.tsx` | Section navigation | Existing `VaultNavigation.tsx` | Keep dense rows, icons, counts, and active state. |
| `frontend/src/components/NotePreview.tsx` | Page-first note view | Existing `NotePreview.tsx`, report components | Show readable Markdown first; move frontmatter to secondary metadata. |
| `frontend/src/components/MetadataPanel.tsx` | Right rail | Existing `MetadataPanel.tsx`, `ReportProvenancePanel.tsx` | Show relationships, annotations, consistency, and rating basis in compact groups. |
| `frontend/src/components/CommandPalette.tsx` | Global search | Existing topbar and API clients | Modal/sheet behavior, 44px rows, grouped results, keyboard-safe layout. |
| `frontend/src/components/KnowledgeGraphPanel.tsx` | Graph inspection | `MetadataPanel.tsx` relationship rows | Functional graph/list hybrid with selectable nodes/edges and provenance. |
| `frontend/src/components/ConsistencyPanel.tsx` | Drift reporting | Report progress/provenance components | Status rows with `synced`, `drift`, and `broken`. |
| `frontend/src/components/RatingBadge.tsx` | Evidence-state badges | Report label rows and status chips | Use approved copy and semantic colors only. |

## Styling Patterns

- Extend `frontend/src/styles/tokens.css` and `frontend/src/styles/app.css`; do not add Tailwind, shadcn, Radix, or registry components.
- Keep cards at 8px radius or less.
- Use `overflow-wrap: anywhere` for UUIDs, paths, URLs, graph labels, and snippets.
- Keep the workspace page-first and dense; do not add a landing page.

