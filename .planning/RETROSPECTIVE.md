# Retrospective

## Milestone: v1.0 — MVP

**Shipped:** 2026-04-18
**Phases:** 5
**Plans:** 29
**Tasks:** 92

### What Was Built

- Local infrastructure, backend contracts, Markdown vault schema/templates, MongoDB/Qdrant repository boundaries, frontend shell, and cross-store documentation.
- TikTok-oriented ingestion with URL submission, local video uploads, transcript/keyframe artifacts, claim extraction, API routes, and React ingestion workbench.
- Ground-truth paper/preprint discovery, candidate dedupe and selection policy, lawful paper acquisition, parsing, Markdown summaries, MongoDB entities/relationships, and Qdrant payload indexing.
- Evidence evaluation with citation validation, versioned Markdown reports, report APIs, reruns, and frontend report inspection.
- Knowledge browser/search/graph/ratings surface with `/knowledge` APIs, command-palette search, graph inspection, consistency checks, annotations, and evidence-state rating badges.

### What Worked

- Phase contracts kept each subsystem focused and made late-stage integration practical.
- Markdown, MongoDB, and Qdrant boundaries stayed explicit enough to add consistency checks without changing the whole storage model.
- Deterministic fallbacks and fake providers kept backend tests offline and stable.
- The page-first browser design gave the knowledge graph a usable interface rather than leaving it as backend-only metadata.

### What Was Inefficient

- `gsd-sdk` was unavailable in this runtime, so execution and milestone archival required manual workflow fallbacks.
- The working tree had unrelated dirty files and generated vault artifacts during closeout, which required careful selective staging.
- Browser dev-server inspection was blocked by sandbox port permissions, so frontend verification relied on production build and static checks.

### Patterns Established

- Canonical generated Markdown remains separate from user annotations.
- Ratings are evidence-state records with approved badge copy and visible basis, not hidden scores.
- Qdrant payloads must preserve UUID, entity type, vault path, source, chunk, and relationship traceability.
- Graph inspection is sourced from MongoDB relationships and enriched with vault paths, not from an external graph runtime.

### Key Lessons

- Keep provider-backed behavior injectable from the start; it pays off in fast offline tests.
- Archive before deleting live planning files; milestone close has too much state movement for shortcuts.
- Generated vault data should be treated as project output, but not blindly staged during planning commits.

### Cost Observations

- Model mix: local Codex orchestration with no external subagents during Phase 5 execution.
- Sessions: one milestone closeout session after Phase 5 execution.
- Notable: context stayed manageable because phase summaries were used for milestone extraction instead of rereading all plans in full.

## Cross-Milestone Trends

| Theme | v1.0 Observation |
|-------|------------------|
| Storage ownership | Markdown as canonical human-readable storage remained the strongest architectural anchor. |
| Verification | Offline deterministic tests made the end-to-end milestone close feasible. |
| UI direction | Page-first knowledge browsing is more useful than graph-first presentation for this product. |
