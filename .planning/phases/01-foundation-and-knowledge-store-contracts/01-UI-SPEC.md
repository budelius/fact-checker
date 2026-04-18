---
phase: 1
slug: foundation-and-knowledge-store-contracts
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-18
---

# Phase 1 - UI Design Contract

> Visual and interaction contract for the Phase 1 frontend shell. This phase creates a React/Vite knowledge-browser skeleton only; ingestion, real reports, search execution, graph visualization, and rating workflows are out of scope.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-react |
| Font | Inter, system-ui, sans-serif |

**Rationale:** Phase 1 should not spend time installing a heavy design system. Use lightweight local components and CSS variables so the later app can either keep the system or migrate to a component library deliberately.

---

## Product Feel

The shell should feel like a focused research workbench: dense enough for knowledge work, calm enough for long reading sessions, and visibly file/entity oriented. It should not look like a landing page, marketing website, or chatbot-first interface.

Primary mental model:

- Left rail: vault/entity navigation.
- Center pane: selected Markdown note or placeholder note.
- Right rail: metadata, linked entities, and source/relationship previews.

The first viewport should show the product itself: the knowledge browser shell, entity navigation, and note preview. Do not build a hero page.

---

## Layout Contract

### Desktop

| Region | Width | Purpose |
|--------|-------|---------|
| App frame | 100vw x 100vh | Fixed application workspace |
| Left rail | 248px | Vault sections and entity counts |
| Main pane | minmax(0, 1fr) | Markdown note preview and entity list placeholder |
| Right rail | 320px | UUID, frontmatter, links, and relationship preview |
| Top bar | 56px height | Product name, current section, future command/search placeholder |

Desktop grid:

```text
top bar spans full width
left rail | main pane | right rail
```

### Tablet

- Left rail remains visible at 220px.
- Right rail collapses into a details panel below the main pane or into a toggleable side panel.
- Main pane keeps priority.

### Mobile

- Use a top bar plus segmented navigation for sections.
- Left rail becomes a drawer or section picker.
- Right rail content appears below the note preview.
- No overlapping panels, no text hidden behind fixed controls.

---

## Navigation Contract

Primary sections must mirror the vault/entity model:

- Videos
- Creators
- Claims
- Papers
- Authors
- Sources
- Evidence
- Reports
- Topics

Phase 1 navigation is static/placeholder. It should demonstrate the future structure and not imply real ingestion or search is already working.

Use icons for navigation items where practical. Each icon must have a text label in the navigation list, because entity categories must stay scannable.

---

## Knowledge Browser Placeholder Content

The shell should include non-functional placeholder examples that communicate the shape of the product:

- A sample note title such as `attention-is-all-you-need`.
- A visible UUID field in frontmatter preview.
- Example frontmatter keys: `uuid`, `entity_type`, `aliases`, `external_ids`, `relationships`, `created_at`, `updated_at`.
- Example wiki links in body text: `[[claims/transformer-attention-scaling]]`, `[[authors/ashish-vaswani]]`.
- Example relationship preview entries: "cites", "supports", "authored_by", "discussed_in".

Placeholder content must be clearly sample data. Do not present generated examples as real fact-checking output.

---

## Spacing Scale

Declared values (all multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, compact metadata rows |
| sm | 8px | Button/icon spacing, rail item padding |
| md | 16px | Default panel padding, form control spacing |
| lg | 24px | Pane gutters, section rhythm |
| xl | 32px | Empty-state spacing, major layout gaps |
| 2xl | 48px | Wide-screen breathing room |
| 3xl | 64px | Rare page-level spacing |

Exceptions: none

---

## Typography

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 15px | 400 | 1.6 |
| Label | 12px | 600 | 1.35 |
| Heading | 24px | 700 | 1.25 |
| Display | 32px | 700 | 1.15 |
| Code/metadata | 13px | 500 | 1.5 |

Rules:

- Letter spacing is `0`.
- Do not scale font size with viewport width.
- Long UUIDs, URLs, and external IDs must wrap or truncate within their panel without causing horizontal overflow.
- Metadata values should use a monospace font stack only where exact identifiers matter.

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#f8faf7` | App background |
| Secondary (30%) | `#ffffff` | Panels, note surface, rails |
| Ink | `#18211f` | Primary text |
| Muted Ink | `#60706a` | Metadata labels and secondary copy |
| Border | `#d8e0dc` | Panel separators and controls |
| Accent (10%) | `#256f62` | Active navigation, focused controls, selected entity |
| Accent Soft | `#dceee9` | Active row background |
| Evidence | `#8a5a00` | Evidence/warning metadata emphasis |
| Destructive | `#b42318` | Destructive actions only |

Accent reserved for:

- Active navigation item
- Focus ring
- Selected entity state
- Primary action in future flows
- Small status marks where selection/active state matters

Rules:

- Do not use a dominant purple/purple-blue gradient palette.
- Do not use decorative gradient orbs, bokeh blobs, or ornamental backgrounds.
- Keep contrast sufficient for metadata-heavy reading.

---

## Component Contracts

### App Shell

- Full-height workspace with top bar, left navigation, main note area, and right details area.
- Stable dimensions for rails and top bar so future dynamic content does not shift layout.

### Navigation Item

- Contains icon, label, optional count.
- Active state uses `Accent Soft` background, `Accent` text/icon, and a left border or inset marker.
- Height: 36px minimum.

### Note Preview

- Looks like a readable Markdown document, not a card inside another card.
- Includes title, entity type, updated timestamp, frontmatter block, body excerpt, and backlink examples.
- Uses a stable max readable line width inside the main pane.

### Metadata Panel

- Shows UUID, slug, entity type, aliases, external IDs, and relationship references.
- Long values wrap cleanly.
- Relationship rows show relation type, target label, and target entity type.

### Empty State

- Use text only or a small icon plus text. No illustration is required.
- Empty state must not explain keyboard shortcuts or internal implementation.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Product label | Fact Checker |
| Section label | Knowledge Vault |
| Primary placeholder CTA | Browse vault |
| Empty state heading | No notes yet |
| Empty state body | New fact checks will create Markdown notes here. |
| Error state | Could not load this note. Check the vault file and try again. |
| Destructive confirmation | Delete note: remove this generated note from the vault? |

Rules:

- Avoid marketing copy.
- Avoid explaining how to use the app inside the UI.
- Use concise labels that fit in navigation and controls.
- Do not claim ingestion, search, graph, or reports work in Phase 1.

---

## Interaction Contract

Phase 1 interactions:

- User can switch between static vault sections.
- User can select a placeholder note/entity.
- User can inspect placeholder frontmatter and relationships.
- UI can show empty and unavailable states for sections without sample entries.

Out of scope for Phase 1:

- Submitting TikTok URLs.
- Running searches.
- Opening real graph visualization.
- Editing Markdown.
- Creating ratings.
- Authenticating users.

---

## Accessibility Contract

- Navigation must be keyboard reachable.
- Active navigation item must be indicated by more than color alone.
- Focus states must be visible and use the accent color.
- Controls must have accessible names.
- Text and metadata must not overflow panels at 320px mobile width.
- Main layout must avoid nested cards and incoherent overlapping panels.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registries | none | not allowed in Phase 1 |

No component registry blocks are approved for Phase 1.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-18
