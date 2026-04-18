# Phase 5: Knowledge Browser, Search, Graph, and Ratings - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md. This log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 05-knowledge-browser-search-graph-and-ratings
**Areas discussed:** Vault Browser Experience, Global Search, Graph Inspection, Ratings Policy, Browser Editability, Rating Badge Tone

---

## Vault Browser Experience

| Option | Description | Selected |
|--------|-------------|----------|
| Database-first | Notion-style tables/lists by entity type, click opens a note detail pane. | |
| Page-first | Mostly readable Markdown/entity pages with light navigation. | yes |
| Workspace hybrid | Notion database plus report/graph/search panels all visible. | |

**User's choice:** Page-first.
**Notes:** User wanted the browser to be more like Notion, but selected the page-first option over database-first.

---

## Global Search

| Option | Description | Selected |
|--------|-------------|----------|
| Command palette | One shortcut/search box for notes, claims, papers, reports, actions. | yes |
| Dedicated search page | Larger search UI with filters and result previews. | |
| Both | Palette for quick jumps, full page for deep research. | |

**User's choice:** Command palette.
**Notes:** Global search should be the primary search interaction.

---

## Graph Inspection

| Option | Description | Selected |
|--------|-------------|----------|
| Use Graphify as product inspiration | Implement our own app graph view using Graphify-like outputs and ideas. | yes |
| Run Graphify as a backend tool | Run Graphify over `vault/` and expose `graph.html`, `graph.json`, and `GRAPH_REPORT.md`. | |
| Try deeper integration | Graphify-generated graph becomes the first graph backend artifact, with MongoDB/Qdrant linked around it. | |

**User's choice:** Use Graphify as product inspiration.
**Notes:** User referenced `https://graphify.net`. The site describes Graphify as an MIT-licensed knowledge graph tool with interactive `graph.html`, queryable `graph.json`, and `GRAPH_REPORT.md` outputs, plus clusters and surprising connections. These are inspiration, not a required Phase 5 runtime dependency.

---

## Ratings Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence profile cards | Label distribution, cited evidence count, confidence, experimental marker, no ranking. | |
| Badges | Simple visual status such as evidence-history badges. | yes |
| Creative but conservative | Let the planner design a richer view as long as every rating is traceable and non-punitive. | |

**User's choice:** Badges.
**Notes:** User initially said "be creative", then selected badge-style display.

---

## Browser Editability

| Option | Description | Selected |
|--------|-------------|----------|
| Read-only browser | View Markdown/frontmatter/relationships, no editing in Phase 5. | |
| Light editing | Allow editing note body/frontmatter from the UI. | |
| Comment/annotation only | Add user notes without rewriting canonical generated notes. | yes |

**User's choice:** Comment/annotation only.
**Notes:** User annotations are allowed, but canonical generated notes should stay separated from user annotations.

---

## Rating Badge Tone

| Option | Description | Selected |
|--------|-------------|----------|
| Evidence state | "strong evidence history", "mixed evidence history", "limited evidence", "insufficient history". | yes |
| Trust-style | "reliable", "mixed", "low confidence", "unknown". | |
| Creative but cautious | Let the planner invent badge language, but avoid punitive labels and show evidence counts. | |

**User's choice:** Evidence state.
**Notes:** Badge copy should describe evidence history rather than trustworthiness.

---

## the agent's Discretion

- Exact page layout within the page-first Notion-like direction.
- Exact command-palette shortcut, grouping, and result ranking.
- Exact graph visualization library and API shape.
- Exact consistency-check severity labels.
- Exact badge visual styling.

## Deferred Ideas

- Runtime Graphify integration over `vault/`.
- Database-first vault tables as the primary browser surface.
- Light editing of generated canonical Markdown notes.
- Trust-style or reputation-style rating copy.
