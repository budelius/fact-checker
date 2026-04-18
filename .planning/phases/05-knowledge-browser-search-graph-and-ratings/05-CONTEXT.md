# Phase 5: Knowledge Browser, Search, Graph, and Ratings - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 5 makes the accumulated Markdown, MongoDB relationship data, and Qdrant vectors useful through browsing, global search, graph inspection, consistency checks, and transparent ratings.

This phase delivers the user-facing knowledge surface for the owned research brain: browse notes, jump across related entities, search stored knowledge, inspect graph relationships, detect store drift, and display conservative evidence-history ratings.

It does not add new ingestion platforms, real-time glasses, meeting assistant behavior, chat-client submission, new source-policy tiers, or hidden aggregate truth scores.

</domain>

<decisions>
## Implementation Decisions

### Vault Browser Experience

- **D-01:** The browser should feel more like Notion than Obsidian's raw graph-first interface.
- **D-02:** Use a page-first experience: readable Markdown/entity pages are the primary surface, not database tables as the first screen.
- **D-03:** Entity navigation should still use the existing vault sections: videos, creators, claims, papers, authors, sources, evidence, reports, topics, and ratings where useful.
- **D-04:** The browser should allow comments or annotations without rewriting canonical generated notes.
- **D-05:** Canonical generated Markdown remains owned system output. User annotations should be stored separately or clearly separated so they do not corrupt generated provenance.

### Global Search

- **D-06:** Global search should be command-palette first.
- **D-07:** The command palette should support quick jumps to notes and entities across the whole brain.
- **D-08:** Search should be global across notes, claims, papers, reports, creators, authors, sources, evidence, topics, and ratings when available.
- **D-09:** The planner can decide whether a deeper dedicated search view is needed, but the locked product direction is a fast global command palette as the primary search UX.

### Graph Inspection

- **D-10:** Use Graphify as product and design inspiration, not as a required Phase 5 runtime dependency.
- **D-11:** The graph UI should learn from Graphify-style outputs: interactive graph view, queryable graph data, human-readable graph report, important nodes, clusters/communities, and surprising cross-domain connections.
- **D-12:** Phase 5 should implement graph inspection around this project's canonical MongoDB relationships and Markdown/Qdrant traceability rather than making Graphify the source of truth.
- **D-13:** The graph surface should be functional and explanatory, not decorative. It should help users answer why a claim, report, paper, creator, author, or source is connected to another.
- **D-14:** Consistency inspection should surface drift between Markdown, MongoDB relationships, and Qdrant payloads in an actionable way.

### Ratings Policy And Display

- **D-15:** Ratings should use badge-style display rather than rankings or punitive scoreboards.
- **D-16:** Badge language should describe evidence state, not personal trust or moral judgment.
- **D-17:** Preferred badge tone: "strong evidence history", "mixed evidence history", "limited evidence", and "insufficient history".
- **D-18:** Badges must be backed by visible evidence counts, label distributions, source basis, and confidence level.
- **D-19:** Early ratings are experimental and conservative until enough evidence history exists.
- **D-20:** Ratings must be traceable to report versions, claim labels, cited evidence, and relationship history. No hidden score is acceptable.

### the agent's Discretion

- Exact page layout, as long as it is page-first, Notion-like, and fits the existing three-pane workbench.
- Exact command-palette keyboard shortcut and result grouping.
- Exact graph layout library, as long as it supports useful relationship inspection and does not turn the graph into decoration.
- Exact consistency-check API shape and drift severity labels.
- Exact rating badge visual styling, as long as badge copy stays evidence-state based and non-punitive.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Phase Requirements

- `.planning/PROJECT.md` - Product vision, owned personal research brain, Graph topology as second signal, storage ownership, and transparency constraints.
- `.planning/REQUIREMENTS.md` - Phase 5 requirements `KB-06`, `UI-03`, `UI-04`, `UI-05`, `RAT-01`, `RAT-02`, and `RAT-03`.
- `.planning/ROADMAP.md` - Phase 5 goal, success criteria, and implementation notes.
- `.planning/STATE.md` - Current project status and Phase 4 handoff.

### Prior Phase Context

- `.planning/phases/01-foundation-and-knowledge-store-contracts/01-CONTEXT.md` - Monorepo, UUID identity, Markdown vault, MongoDB graph-like relationship store, Qdrant payload traceability, and Obsidian-first vault decisions.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md` - Video, transcript, screenshot, claim, and source-candidate handoff contracts.
- `.planning/phases/03-ground-truth-discovery-and-paper-processing/03-CONTEXT.md` - Paper/source/author/evidence records, selected/rejected source decisions, chunk traceability, and rejected-candidate provenance.
- `.planning/phases/04-evidence-evaluation-and-fact-check-reports/04-CONTEXT.md` - Report labels, versioning, citations, provenance, and explicit boundary against ratings.

### Existing Docs And Contracts

- `docs/phase-1-contracts.md` - UUID, Markdown, MongoDB, Qdrant, logging, frontend shell, and safety contracts.
- `docs/phase-4-evaluation.md` - Report routes, evidence policy, MongoDB relationships, versioning, and frontend report UI behavior.
- `vault/SCHEMA.md` - Vault folders, frontmatter, raw/wiki split, relationship conventions, slug rules, and safety constraints.

### Existing Code Contracts

- `backend/app/schemas/entities.py` - Canonical entity types including `rating`, `topic`, `report`, `evidence`, and all browsable knowledge objects.
- `backend/app/schemas/relationships.py` - Relationship types and relationship record shape for graph inspection.
- `backend/app/schemas/vector_payloads.py` - Qdrant payload fields used for search filters and traceability.
- `backend/app/repositories/mongo.py` - MongoDB entity and relationship collections that Phase 5 should browse and validate.
- `backend/app/repositories/qdrant.py` - Qdrant upsert boundary and deterministic point ID behavior.
- `backend/app/api/reports.py` - Report API route pattern and stored report payloads.
- `frontend/src/components/AppShell.tsx` - Existing three-pane shell and right-rail pattern.
- `frontend/src/components/VaultNavigation.tsx` - Existing vault section navigation.
- `frontend/src/components/NotePreview.tsx` - Existing placeholder note preview to evolve into the page-first browser.
- `frontend/src/components/MetadataPanel.tsx` - Existing metadata/right-rail pattern.
- `frontend/src/components/reports/` - Existing report page components and provenance UI.
- `frontend/src/data/sampleVault.ts` - Current vault section and sample note types.
- `frontend/src/styles/app.css` and `frontend/src/styles/tokens.css` - Existing dense research-workbench styling.

### External Conceptual Reference

- `https://graphify.net/` - Graphify reference for graph product ideas: interactive `graph.html`, queryable `graph.json`, human-readable `GRAPH_REPORT.md`, clusters, important nodes, and surprising relationships. Use as inspiration only; do not make Graphify a required runtime dependency unless planning explicitly justifies a spike.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `frontend/src/components/AppShell.tsx`: Existing three-pane layout with left vault navigation, central main pane, and right metadata/provenance rail.
- `frontend/src/components/VaultNavigation.tsx`: Existing entity-section navigation can become the Phase 5 vault browser sidebar.
- `frontend/src/components/NotePreview.tsx`: Existing Markdown/frontmatter preview can evolve into the page-first note browser.
- `frontend/src/components/MetadataPanel.tsx`: Existing right-rail metadata pattern can show note metadata, relationships, annotations, consistency status, and rating basis.
- `frontend/src/components/reports/`: Existing report components provide label, evidence, citation, provenance, and version UI patterns to reuse.
- `backend/app/repositories/mongo.py`: Entity and relationship collections are the natural source for browse and graph APIs.
- `backend/app/repositories/qdrant.py`: Qdrant repository is the natural source for vector-backed search.
- `backend/app/schemas/vector_payloads.py`: Payload fields already include entity type, vault path, source, source UUID, and relationship UUIDs for filtered search.

### Established Patterns

- The app uses React, TypeScript, Vite, Yarn, and a dense research-workbench visual language.
- Backend APIs are FastAPI routes with Pydantic schemas and route-local stores where earlier phases used in-memory job stores.
- UUIDs are canonical identity across Markdown, MongoDB, Qdrant, and API payloads.
- Markdown is the human-readable canonical layer; MongoDB and Qdrant must remain traceable to it.
- Existing report UI renders backend-provided truth labels and does not compute ratings or truth scores in the frontend.

### Integration Points

- Add backend browse/search/graph/rating APIs that read from vault Markdown, MongoDB entities/relationships, and Qdrant payloads.
- Extend `AppShell` from ingestion/report workbench into a vault browser surface without losing the existing ingestion/report flow.
- Add a command palette for global search and quick jumps.
- Add consistency-check services that compare Markdown frontmatter/body links, MongoDB entities/relationships, and Qdrant payload records.
- Add rating records as auditable derived knowledge with badge-style UI and visible evidence basis.

</code_context>

<specifics>
## Specific Ideas

- The vault should feel more like Notion: readable pages, clean navigation, and approachable knowledge browsing rather than a raw Markdown editor.
- Global search should be a command palette.
- Graphify is a useful conceptual reference for graph inspection, especially graph artifacts, report-like summaries, clusters, important nodes, and surprising connections.
- The graph should support the project's "second signal" idea: relationships across the brain help surface corroboration and contradiction beyond a single report.
- User annotations are allowed, but canonical generated notes should not be rewritten directly through the browser in Phase 5.
- Rating badges should describe evidence state, not trustworthiness or reputation in a punitive sense.

</specifics>

<deferred>
## Deferred Ideas

- Runtime Graphify integration over `vault/` is not selected for Phase 5 by default. It can be revisited as a spike if planning finds it useful, but the locked direction is Graphify-inspired product behavior over this app's canonical data.
- Database-first Notion tables are not the primary Phase 5 browser direction. Tables/lists can exist as secondary views if useful.
- Light editing of canonical generated Markdown notes is not selected. Phase 5 should prefer annotations/comments that preserve generated-note provenance.
- Trust-style rating copy such as "reliable" or "low trust" is not selected because it can become punitive or opaque.

</deferred>

---

*Phase: 05-knowledge-browser-search-graph-and-ratings*
*Context gathered: 2026-04-18*
