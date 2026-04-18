---
phase: 5
slug: knowledge-browser-search-graph-and-ratings
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-18
reviewed_at: 2026-04-18
---

# Phase 5 - UI Design Contract

Visual and interaction contract for the knowledge browser, global search, graph inspection, consistency checks, and evidence-state ratings.

Phase 5 turns the accumulated owned knowledge into the main product surface. It should feel like a focused Notion-style research workspace: readable pages first, fast global jumping, visible source trails, and conservative ratings that describe evidence history without becoming reputation scoring.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none; extend the existing CSS token system in `frontend/src/styles/tokens.css` |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-react |
| Font | Inter, system-ui, sans-serif; mono values use SFMono-Regular, Consolas, Liberation Mono |

Notes:

- Extend the existing React/Vite/Yarn app shell. Do not introduce shadcn, Radix, Tailwind, or a new design system in Phase 5 unless a later plan explicitly justifies a narrow dependency.
- Preserve the three-pane knowledge workspace: left vault navigation, central page-first browser, right metadata/provenance/annotation rail.
- Keep the experience dense, calm, and research-oriented. The first screen is the usable vault browser, not a landing page or feature explainer.
- Use icons for commands: search, graph, copy, open link, annotation, consistency status, and rating basis. Use text buttons only for clear verbs such as `Add annotation`.
- Cards remain 8px radius or less. Do not nest cards inside cards; use rows, panels, and full-width sections instead.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, badge padding, inline metadata separators |
| sm | 8px | Navigation rows, compact relationship rows, command result gaps |
| md | 16px | Page blocks, annotation form rows, graph side-panel groups |
| lg | 24px | Browser section padding, right-rail groups, search result sections |
| xl | 32px | Main pane padding, page-to-panel separation |
| 2xl | 48px | Empty state vertical rhythm and graph/report separation only |
| 3xl | 64px | Mobile single-column page breaks only |

Exceptions:

- Existing `--topbar-height` remains 56px.
- Existing left rail width remains 248px.
- Right rail may grow from 320px to 360px only if graph/rating provenance becomes unreadable at 320px.
- Command palette rows and icon buttons must keep a 44px minimum hit target.
- Relationship rows, search results, rating badges, and consistency rows must use stable dimensions so long UUIDs, labels, or counts do not shift the layout.

---

## Typography

Use the current type scale and avoid viewport-scaled font sizes.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 15px | 400 | 1.6 |
| Label | 12px | 600 | 1.35 |
| Heading | 24px | 600 | 1.25 |
| Display | 32px | 600 | 1.15 |

Rules:

- Use 32px display text only for the active note/entity title.
- Use 24px headings for page sections such as `Summary`, `Evidence trail`, `Related claims`, `Graph`, `Annotations`, and `Rating basis`.
- Use 12px mono text for UUIDs, Qdrant point IDs, chunk IDs, relationship UUIDs, and vault paths.
- All UUIDs, URLs, vault paths, chunk IDs, search snippets, and graph node labels must wrap with `overflow-wrap: anywhere`.
- Letter spacing is 0. Do not use negative tracking.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#f8faf7` | App background and broad workspace area |
| Secondary (30%) | `#ffffff` | Topbar, rails, note surfaces, command palette, graph side panels |
| Accent (10%) | `#256f62` | Primary action, active navigation, selected search result, focus rings |
| Destructive | `#b42318` | Broken consistency status, failed sync/checks, destructive actions only |

Existing semantic colors:

| Token | Value | Usage |
|-------|-------|-------|
| `--color-accent-soft` | `#dceee9` | Active note, selected command result, strong evidence-history badge background |
| `--color-evidence` | `#8a5a00` | Mixed evidence-history badge, graph surprise/important connection indicator |
| `--color-muted` | `#60706a` | Limited/insufficient evidence-history badges, secondary metadata |
| `--color-border` | `#d8e0dc` | Panel boundaries, note block separators, relationship rows |

Evidence-state badge mapping:

| Badge | Foreground | Background | Border |
|-------|------------|------------|--------|
| `strong evidence history` | `#256f62` | `#dceee9` | `#256f62` |
| `mixed evidence history` | `#8a5a00` | `#fff7df` | `#8a5a00` |
| `limited evidence` | `#60706a` | `#f8faf7` | `#d8e0dc` |
| `insufficient history` | `#60706a` | `#eef2f6` | `#c7d0dc` |

Consistency status mapping:

| Status | Foreground | Background | Meaning |
|--------|------------|------------|---------|
| `synced` | `#256f62` | `#dceee9` | Markdown, MongoDB, and Qdrant agree |
| `drift` | `#8a5a00` | `#fff7df` | Non-blocking mismatch needs review |
| `broken` | `#b42318` | `#fff7f5` | Missing canonical record or broken relationship |

Accent reserved for:

- `Add annotation`
- Active vault navigation item
- Selected command palette row
- Focus-visible outlines
- Selected graph node/edge
- Strong evidence-history badge

Do not introduce a broad new color palette. Use green, amber, red, and neutral only where they carry explicit status meaning.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | Add annotation |
| Command palette placeholder | Search the vault or jump to an entity |
| Empty state heading | No note selected |
| Empty state body | Choose a vault page or search the brain to inspect stored evidence. |
| Browser loading state | Loading vault page |
| Search empty state | No matching knowledge found |
| Search empty body | Try a claim, paper title, creator, report UUID, or source URL. |
| Graph empty state | No relationships recorded yet |
| Graph empty body | This page has no stored relationships to inspect. |
| Consistency check CTA | Check consistency |
| Consistency success | Markdown, MongoDB, and Qdrant are in sync. |
| Annotation empty state | No annotations yet |
| Annotation body | Add a separate user note without changing the generated Markdown. |
| Error state | This knowledge view could not load. Keep the UUID and retry after checking the backend logs. |
| Destructive confirmation | none; Phase 5 must not add delete or purge actions without a later explicit plan |

Forbidden copy:

- Do not use `truth score`, `reputation score`, `trust score`, `reliable creator`, `unreliable creator`, or punitive ranking language.
- Do not call Graphify a runtime dependency. It is an inspiration/reference unless a later spike changes that decision.
- Do not say annotations edit canonical notes. They are separate from generated Markdown.

Required badge copy:

- `strong evidence history`
- `mixed evidence history`
- `limited evidence`
- `insufficient history`
- `experimental`

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registry | none | blocked unless explicitly approved in a later plan |

No registry components are approved for Phase 5. If planning proposes a graph visualization library, it must be installed as a normal dependency with explicit evaluation, not copied from an opaque UI registry.

---

## Phase 5 Interaction Contract

### Shell Placement

| Area | Contract |
|------|----------|
| Topbar | Keep brand on the left. Section label should read `Knowledge vault` when the browser is active. Provide a search icon button that opens the command palette. |
| Left rail | Preserve vault sections and counts. Add ratings only when rating records exist or a placeholder section is needed for Phase 5. |
| Main pane | Page-first note/entity browser. The selected page title, entity type, readable body, backlinks, related entities, graph preview, and rating badge appear here. |
| Right rail | Metadata, relationship details, annotations, consistency status, and rating basis. On mobile this rail moves below the page. |

### Page-First Vault Browser

| Element | Contract |
|---------|----------|
| Default view | A readable selected note/entity page, not a table. |
| Page title | Large readable title with entity type and updated timestamp nearby. |
| Body | Render generated Markdown content as readable sections. Do not show a raw machine dump as the primary content. |
| Frontmatter | Available in a collapsed or secondary metadata view; not the first thing users read. |
| Relationships | Show readable relationship rows with entity labels, types, and direction. |
| Backlinks | Show links from claims, papers, reports, creators, authors, sources, and evidence when known. |
| Raw paths | Vault paths are visible in mono text and copyable. |
| Generated note boundary | Clearly separate system-generated content from user annotations. |

### Annotation Contract

| Element | Contract |
|---------|----------|
| Action | `Add annotation` in the right rail or page toolbar. |
| Storage model | User annotations are separate records or clearly separated Markdown blocks. They must not rewrite generated canonical note body/frontmatter. |
| Display | Annotation list shows author/source as `user`, timestamp, and linked entity UUID. |
| Safety | Annotation text is user content and must not be treated as source evidence unless a later source-policy phase says so. |
| Editing | Phase 5 may allow editing annotations, but not generated notes. |

### Command Palette Search

| Element | Contract |
|---------|----------|
| Trigger | Search icon button in topbar; planner may add `Cmd/Ctrl+K`. |
| Placeholder | `Search the vault or jump to an entity` |
| Scope | Global across notes, entities, reports, claims, papers, authors, creators, sources, evidence, topics, and ratings. |
| Results | Group by entity type. Each result shows title, entity type, vault path or source, and one relevant snippet. |
| Actions | Select result to open the page. Secondary actions may copy UUID or open source link. |
| Filters | Command palette may include quick filters such as `type:paper`, `type:claim`, or label chips if planning can keep it simple. |
| Empty state | Use the search empty copy from this contract. |

### Graph Inspection

| Element | Contract |
|---------|----------|
| Inspiration | Graphify-style interactive graph, queryable graph data, graph report, important nodes, clusters, and surprising cross-domain connections. |
| Source of truth | MongoDB relationships and Markdown/Qdrant traceability, not Graphify runtime output. |
| Main use | Explain relationship trails around the selected entity. |
| Node labels | Show readable titles first, UUIDs second. Long labels must wrap or truncate with accessible title text. |
| Edge labels | Show relationship type: `cites`, `supports`, `contradicts`, `authored_by`, `discussed_in`, `derived_from`, `related_to`. |
| Layout | Graph can be compact in the main pane with details in the right rail. It must not be decorative full-screen art. |
| Details | Selecting a node or edge shows provenance, UUIDs, source report/version, and related vault paths. |
| Clusters | If implemented, clusters should be named around entity/topic labels and used to explain domains. |
| Surprise links | If implemented, use restrained amber styling and explain why the connection is unexpected or useful. |

### Consistency Check

| Element | Contract |
|---------|----------|
| Trigger | `Check consistency` command in the page toolbar or command palette. |
| Scope | Markdown frontmatter/body wiki links, MongoDB entity/relationship records, and Qdrant payloads. |
| Summary | Show counts for checked notes, missing MongoDB records, missing Qdrant payloads, broken relationships, and orphan vectors. |
| Severity | Use `synced`, `drift`, and `broken`. |
| Detail rows | Each row includes affected UUID, entity type, store, issue, and suggested repair direction. |
| No auto repair | Phase 5 UI may surface repair directions but should not silently mutate stores without a later explicit plan. |

### Evidence-State Ratings

| Element | Contract |
|---------|----------|
| Display | Badge-style rating near entity title and in right rail. |
| Entities | Creators, papers, authors, and sources. |
| Badge text | `strong evidence history`, `mixed evidence history`, `limited evidence`, `insufficient history`. |
| Experimental marker | Early ratings include `experimental`. |
| Basis | Show evidence count, claim label distribution, cited report versions, source basis, and confidence level. |
| No hidden score | If any numeric confidence is shown, it must be paired with visible evidence basis and never become a standalone ranking. |
| Tone | Evidence history, not trustworthiness. Avoid reputational or punitive language. |

### Mobile Layout

| Area | Contract |
|------|----------|
| Left rail | Collapses into horizontal section navigation or a menu. |
| Main page | Remains readable, page-first, with annotations and graph below content. |
| Command palette | Full-width modal/sheet with 44px result rows. |
| Graph | Defaults to relationship list or simplified graph preview to avoid cramped node overlap. |
| Right rail | Moves below selected page content. |

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-18
