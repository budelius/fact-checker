---
phase: 4
slug: evidence-evaluation-and-fact-check-reports
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-18
reviewed_at: 2026-04-18
---

# Phase 4 - UI Design Contract

Visual and interaction contract for evidence evaluation and fact-check reports. Generated inline from Phase 4 context and verified against the existing frontend workbench.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none; use existing CSS token system in `frontend/src/styles/tokens.css` |
| Preset | not applicable |
| Component library | none |
| Icon library | lucide-react |
| Font | Inter, system-ui, sans-serif; mono values use SFMono-Regular, Consolas, Liberation Mono |

Notes:

- Extend the existing React/Vite/Yarn AppShell and ingestion workbench. Do not create a marketing page, landing page, or disconnected route.
- Keep the current research workbench feel: dense, source-oriented, traceable, and optimized for reading evidence quickly.
- Use the existing three-pane shell: left vault navigation, main report workspace, right provenance/metadata rail.
- No shadcn, Radix, Tailwind, or new design system dependency should be introduced in Phase 4.

---

## Spacing Scale

Declared values (must be multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, badge padding, citation separators |
| sm | 8px | Compact row gaps, label chips, citation chips |
| md | 16px | Claim row padding, evidence snippet spacing, form rows |
| lg | 24px | Report section padding, provenance rail groups |
| xl | 32px | Main pane padding, major report groups |
| 2xl | 48px | Version history separation or empty state vertical space only |
| 3xl | 64px | Page-level spacing only in single-column mobile layout |

Exceptions:

- Existing `--topbar-height` remains 56px.
- Existing rail widths remain 248px left and 320px right unless the planner needs the right rail at 360px for provenance readability on desktop.
- New mobile controls must keep a 44px minimum touch target.
- Border radius remains 8px maximum.
- Evidence snippets, claim rows, version rows, and citation lists must use stable row spacing so badge or label changes do not shift the layout unexpectedly.

---

## Typography

Use the same type scale as Phase 2 additions. Use only weights 400 and 600 in new UI.

| Role | Size | Weight | Line Height |
|------|------|--------|-------------|
| Body | 15px | 400 | 1.6 |
| Label | 12px | 600 | 1.35 |
| Heading | 24px | 600 | 1.25 |
| Display | 32px | 600 | 1.15 |

Rules:

- Use the mono font family only at declared sizes: 12px for UUIDs, chunk IDs, version IDs, timestamps, and provider names; 15px for readable raw-value rows.
- Keep letter spacing at 0 except existing uppercase micro-labels, which may keep browser-default spacing with no negative tracking.
- Long URLs, UUIDs, chunk IDs, claim text, transcript excerpts, and citation snippets must wrap with `overflow-wrap: anywhere`.
- Report headings should name the current artifact or state, such as "Fact-check report", "Narrative report", "Claims checked", "Evidence used", and "Provenance".

---

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#f8faf7` | App background and broad workspace area |
| Secondary (30%) | `#ffffff` | Topbar, rails, report surface, claim rows, evidence panels |
| Accent (10%) | `#256f62` | Primary CTA, supported label, active progress step, focus rings, selected citation linkage |
| Destructive | `#b42318` | Contradicted label, failed report generation, destructive actions only |

Existing semantic colors:

| Token | Value | Usage |
|-------|-------|-------|
| `--color-accent-soft` | `#dceee9` | Supported label background, selected row background, linked citation highlight |
| `--color-evidence` | `#8a5a00` | Mixed label, evidence/source clue chips, news-exception badge |
| `--color-muted` | `#60706a` | Insufficient label, secondary metadata, old report versions |
| `--color-border` | `#d8e0dc` | Panel boundaries, separators, claim/evidence rows |

Label mapping:

| Label | Foreground | Background | Border |
|-------|------------|------------|--------|
| `supported` | `#256f62` | `#dceee9` | `#256f62` |
| `contradicted` | `#b42318` | `#fff7f5` | `#b42318` |
| `mixed` | `#8a5a00` | `#fff7df` | `#8a5a00` |
| `insufficient` | `#60706a` | `#f8faf7` | `#d8e0dc` |

Accent reserved for:

- Primary CTA: `Generate report`
- `supported` status and supported citation links
- Active report generation step
- Active version in version history
- Focus-visible outlines
- Selected claim/evidence linkage

Do not introduce a broad new color palette in Phase 4. If extra status color is needed, derive it from the existing tokens above.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary CTA | Generate report |
| Rerun CTA | Rerun report |
| Empty state heading | Generate a report from selected evidence |
| Empty state body | Run evidence evaluation after paper discovery completes to create a cited Markdown report for this video. |
| Error state | This report could not be generated. Review the failed step, keep the job UUID, and rerun after fixing the source evidence. |
| Destructive confirmation | none; Phase 4 must not add delete, purge, or destructive report actions |

Additional required labels:

| Element | Copy |
|---------|------|
| Topbar section | Fact-check report |
| Narrative section | Narrative report |
| Claim section | Claims checked |
| Evidence section | Evidence used |
| Unused evidence section | Candidate evidence reviewed |
| Version section | Report versions |
| Provenance rail heading | Provenance |
| Rerun availability | Rerun available |
| No report copy | No fact-check report generated yet. |
| Citation label | Citation |
| Paper summary warning | Paper summaries are navigation only and were not used as verdict evidence. |
| News exception label | Non-scientific source exception |
| Insufficient uncertainty label | Why evidence is insufficient |
| Mixed uncertainty label | Why evidence is mixed |

Do not use copy that implies a creator-level truth score, global reputation score, or punitive rating in Phase 4. Avoid "verified creator", "truth score", "reputation", and "rating" except when explicitly stating those are Phase 5.

---

## Phase 4 Interaction Contract

### Shell Placement

| Area | Contract |
|------|----------|
| Topbar | Keep brand on the left. Set section label to `Fact-check report` while the Phase 4 report view is active. Keep `Browse vault` as a secondary command. |
| Left rail | Preserve vault-oriented navigation and keep `Reports` visible as a canonical section. Do not replace the vault rail with report filters. |
| Main pane | First viewport should show report generation state or the narrative report first. Claim details follow the narrative. |
| Right rail | Show report metadata, version history, cited evidence counts, unused candidate evidence counts, source policy notes, and selected claim/evidence provenance. On mobile this content moves below the report. |

### Report Generation Flow

| State | Required UI |
|-------|-------------|
| Not ready | Explain that paper discovery must complete before report generation. Show current ingestion/ground-truth job UUIDs if available. |
| Ready | Show `Generate report`, selected claim count, selected paper/chunk count, and a warning that generated paper summaries are navigation only. |
| Running | Show a progress list with current operation; never use a generic spinner as the only indicator. |
| Complete | Show narrative report first, then compact claim details, citations, provenance, Markdown report path, and version number. |
| Failed | Keep the failed step visible, preserve job/report UUIDs, show recoverable error copy, and allow rerun. |
| Rerun available | Show a visible `Rerun available` notice when new papers or chunks appear for an already evaluated claim. The old report remains stable. |

### Progress Steps

Use a compact vertical timeline on desktop and a stacked list on mobile.

| Step | Display Label | Operation Examples | Terminal Artifact |
|------|---------------|--------------------|-------------------|
| 1 | Load claims | Loading extracted video claims and transcript context | claim set |
| 2 | Load evidence | Loading selected paper chunks and source links | evidence retrieval set |
| 3 | Select citations | Choosing cited chunks and candidate unused chunks | citation candidates |
| 4 | Evaluate claims | Decomposing claims, checking overclaims, assigning labels | claim evaluations |
| 5 | Validate citations | Rejecting uncited non-insufficient labels | validated evaluation |
| 6 | Write report | Writing Markdown report and structured provenance | report artifact |
| 7 | Index and link | Writing MongoDB relationships and optional vector payloads | report entity/relationships |

Each step must show one of: `pending`, `running`, `complete`, `failed`, or `skipped`. `skipped` is allowed only for optional indexing/linking work when a dependency is unavailable.

### Narrative Report

| Element | Contract |
|---------|----------|
| Placement | First completed-report content in the main pane. |
| Content | Short readable narrative summary of the video's evidence situation, not a claim table first. |
| Tone | Cautious, source-grounded, and explicit about limits. |
| Source policy | Mention when the run used only papers/preprints or when the rare news exception was used. |
| Report path | Show Markdown report vault path in mono text with a copy-icon button. |

### Claim Details

| Element | Contract |
|---------|----------|
| Row layout | One row per claim with label chip, compact rationale, citation chips, and timestamp/source context. |
| Default density | Compact by default: verdict, one or two sentence rationale, citations. |
| Subclaims | If the backend provides subclaims, show count and allow expansion. Do not expand all subclaims by default. |
| Overclaim handling | When overclaiming changes the label, show a short `overclaim` note in the claim row. |
| Uncertainty | Show uncertainty text only for `mixed` and `insufficient` labels. |
| Insufficient | Explain which direct evidence was missing; do not show generic "not enough data" copy. |
| Mixed | Explain which parts were supported and which parts were not. |

### Evidence And Citations

| Element | Contract |
|---------|----------|
| Citation chip | Shows paper title or source label, chunk ID, page/section if available, and link affordance. |
| Evidence snippet | Shows source text excerpt from raw chunk/direct source text, never a generated paper summary. |
| Source link | External source link opens in a normal link target and is visually secondary to the evidence snippet. |
| Paper summary warning | When a report includes paper context, show that summaries were navigation only and not verdict evidence. |
| News exception | If used, show `Non-scientific source exception` with article title/source link and do not style it as paper ground truth. |
| Unused candidates | Right rail or provenance section shows cited chunks plus rejected/unused candidate chunks, matching the Phase 4 traceability decision. |

### Versioning And Reruns

| Element | Contract |
|---------|----------|
| Version display | Show report version number, created timestamp, and report UUID. |
| Version history | Right rail lists versions newest first with stable UUID/path links. |
| Rerun available | Notice appears when new papers/chunks exist for already evaluated claims. |
| Rerun action | `Rerun report` creates a new version; it must not overwrite the active version. |
| Historical stability | Old versions remain readable and marked as historical when a newer version exists. |

### Markdown Report Linkage

The UI must show the Markdown report path and make report content align with the vault contract:

- `vault/wiki/reports/{slug}.md`
- frontmatter with report UUID, source video UUID, claim UUIDs, cited evidence UUIDs, version, created/updated timestamps, and provenance references
- body sections for Narrative report, Claims checked, Evidence used, Candidate evidence reviewed, and Provenance

---

## Component Inventory

| Component | Purpose | Notes |
|-----------|---------|-------|
| `AppShell` | Existing three-pane workbench shell | Extend, do not replace. |
| `IngestionWorkbench` | Existing job/claim context view | Attach report generation/display after ingestion and ground-truth completion. |
| `ReportGenerationPanel` | Readiness, generation CTA, progress, and recoverable errors | New Phase 4 component. |
| `ReportStatusHeader` | Report UUID, version, lifecycle status, Markdown path | New Phase 4 component. |
| `ReportProgressTimeline` | Step-by-step evaluation progress | Can reuse/parallel `ProgressTimeline` pattern. |
| `NarrativeReport` | Narrative-first report content | New Phase 4 component. |
| `ClaimEvaluationList` | Compact evaluated claim rows | Extends the claim row visual pattern. |
| `ClaimEvaluationRow` | Label, rationale, citations, uncertainty when needed | New Phase 4 component. |
| `CitationList` | Citation chips and source links | New Phase 4 component. |
| `EvidenceSnippet` | Raw cited chunk/direct source text excerpt | New Phase 4 component. |
| `ReportProvenancePanel` | Version history, cited/unused chunks, source policy notes | New Phase 4 right-rail component. |
| `ReportVersionList` | Stable report versions and rerun availability | New Phase 4 component. |

No component may use generated paper summaries as displayed verdict evidence. Components consume normalized report/evaluation API payloads and should not know provider-specific implementation details.

---

## Accessibility And Responsive Contract

- `Generate report` and `Rerun report` must be real buttons with accessible labels.
- Report progress updates must use `aria-live="polite"`.
- Blocking failures must use `role="alert"`.
- Label chips must not rely on color alone; include visible text `supported`, `contradicted`, `mixed`, or `insufficient`.
- Citation chips and copy-icon buttons must have accessible labels and tooltips.
- Evidence snippets must render untrusted source text as plain text only. Never render paper, transcript, OCR, or news article content as HTML.
- Keyboard focus order should follow: report action/status, narrative report, claim list, selected evidence/provenance rail.
- Mobile layout below 720px keeps topbar stacked, vault navigation horizontal, report main pane first, and provenance metadata below the report.
- Text must never overlap badges, citation chips, thumbnails, or buttons. Use wrapping, fixed preview dimensions, and stable row layouts.
- Minimum mobile touch target is 44px for report actions, expand/collapse controls, citation links, copy buttons, and version selectors.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none | not required |
| third-party registry | none | blocked for Phase 4 |

Do not add a component registry dependency in Phase 4. If a future phase adds one, it must go through a separate registry review.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-04-18

## Inline Verification Notes

- Copywriting matches Phase 4 context: narrative-first, compact claim details, no truth scores, no ratings.
- Visuals preserve the existing dense workbench and three-pane shell.
- Color uses existing tokens and maps claim labels without adding a new palette.
- Typography and spacing match the Phase 2 UI-SPEC and current CSS token scale.
- Registry safety is clear: no shadcn, Radix, Tailwind, or third-party registry in this phase.
