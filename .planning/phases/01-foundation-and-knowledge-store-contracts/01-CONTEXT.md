# Phase 1: Foundation and Knowledge Store Contracts - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 establishes the monorepo skeleton, local datastore setup, foundational schemas, Markdown vault conventions, storage boundaries, and minimal frontend shell that all later phases will build on. It does not implement real TikTok ingestion, fact-checking, paper search, evidence evaluation, ratings, or graph visualization beyond contracts, placeholders, and schema-level foundations.

</domain>

<decisions>
## Implementation Decisions

### Project Shape

- **D-01:** Use a monorepo.
- **D-02:** Use `frontend/` for the web app.
- **D-03:** Use React, TypeScript, Vite, and Yarn for the frontend.
- **D-04:** Use `backend/` for the backend service. Python/FastAPI remains the assumed backend stack from project research unless the user changes it later.
- **D-05:** Use `vault/` for the owned Markdown knowledge base.
- **D-06:** Use `infra/` for Docker Compose, service configuration, migrations, and local infrastructure files.
- **D-07:** Keep Docker Compose simple in Phase 1. Default Compose should run datastores only; backend/frontend can run on the host during development.

### Datastores

- **D-08:** Use MongoDB as the primary app metadata database.
- **D-09:** MongoDB replaces both Postgres and Neo4j for v1 foundation.
- **D-10:** Qdrant remains the vector database target.
- **D-11:** Dedicated graph database work is deferred. Graph-like relationships should be modeled in MongoDB first.
- **D-12:** Treat this as an explicit override of the initial project research and roadmap text that named Postgres and Neo4j.

### Knowledge IDs

- **D-13:** Use UUIDs everywhere for canonical entity identity.
- **D-14:** Every canonical entity gets a UUID: video, creator, transcript, screenshot/keyframe, claim, source, paper, author, evidence chunk, report, rating, topic, relationship record, and any future canonical knowledge object.
- **D-15:** External identifiers such as TikTok video IDs, usernames, DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, URLs, and provider IDs are metadata or aliases, not primary IDs.
- **D-16:** Markdown files must include UUID in YAML frontmatter. MongoDB, Qdrant, and the vault refer to the same object through that UUID.
- **D-17:** Human-readable Markdown filenames use slugs only. UUIDs live in frontmatter, not filenames.
- **D-18:** Phase 1 planning must define slug collision handling and rename/link stability behavior because slugs are not canonical identity.

### Markdown Vault

- **D-19:** Optimize the vault for Obsidian-first use.
- **D-20:** Use folder-per-entity-type organization.
- **D-21:** Use YAML frontmatter for UUID, entity type, aliases/external IDs, timestamps, source links, and relationship references.
- **D-22:** Notes should be pleasant to read manually, not just machine dumps.
- **D-23:** Use readable Obsidian-style wiki links in note bodies where useful.
- **D-24:** Represent relationships with both frontmatter UUID references and readable wiki links in the body.
- **D-25:** MongoDB and Qdrant indexes are derived from or synchronized with vault/schema data; they do not replace the human-readable Markdown layer.

### LLM Wiki Influence

- **D-26:** Apply the Karpathy LLM Wiki pattern where useful: split raw sources, generated wiki, and schema/maintenance instructions.
- **D-27:** Raw sources are immutable evidence inputs. The system may read from them, but should not rewrite them.
- **D-28:** Generated wiki notes are the maintained Markdown knowledge layer. The app/LLM pipeline can create and update these notes as new sources and reports arrive.
- **D-29:** The schema and maintenance contract should live in project instructions and vault conventions so future agents know how to ingest, query, and lint the wiki.
- **D-30:** Add `vault/index.md` as a content-oriented catalog that helps humans and agents navigate the vault.
- **D-31:** Add `vault/log.md` as an append-only chronological record of ingests, queries, lint passes, and notable maintenance actions.
- **D-32:** Plan for a future vault lint workflow that checks broken links, orphan notes, missing UUIDs, MongoDB/Qdrant drift, stale claims, and contradictions.

### Provider and Store Boundaries

- **D-33:** Use pragmatic direct clients first in Phase 1 rather than strict provider adapters from day one.
- **D-34:** Direct SDK/client usage is allowed for speed, especially inside repository/service modules.
- **D-35:** External calls must still live in obvious modules and must not be scattered through routes, UI components, or unrelated code.
- **D-36:** MongoDB and Qdrant can use direct clients behind repository/service modules.
- **D-37:** OpenAI, TikTok, paper APIs, transcription, and embeddings do not need full abstract provider interfaces in Phase 1, but any stubs/config should be isolated enough to wrap later.
- **D-38:** Secrets must stay in environment/config and never enter Markdown, logs, commits, or generated notes.
- **D-39:** Phase 1 should avoid implementing real TikTok/OpenAI/paper API behavior beyond config stubs or placeholders unless needed for store contracts.

### Minimal UI Shell

- **D-40:** Build a minimal React/Vite frontend shell oriented around the knowledge browser.
- **D-41:** Include app navigation.
- **D-42:** Include a placeholder Obsidian-like knowledge browser layout.
- **D-43:** Align placeholder browser sections with the vault entity folders: videos, creators, claims, papers, authors, sources, evidence, reports, and topics.
- **D-44:** Do not implement real ingestion or report flows in Phase 1. Those belong to later phases.
- **D-45:** A service dashboard is not required in Phase 1 unless the planner finds it necessary for quick local health checks.

### the agent's Discretion

- Exact Docker Compose file organization and naming.
- Exact backend package manager and Python project tooling, as long as it fits the Python/FastAPI assumption and repo conventions.
- Exact MongoDB collection names, as long as UUID identity and relationship contracts are clear.
- Exact Qdrant collection naming, as long as payloads include UUID/entity metadata and can trace chunks back to canonical notes or source records.
- Exact visual styling of the placeholder knowledge browser, as long as it respects the product's research/workbench feel and does not become a marketing landing page.

</decisions>

<specifics>
## Specific Ideas

- The frontend should be React, TypeScript, Vite, and Yarn.
- The repo should be a monorepo.
- Docker Compose should stay simple.
- MongoDB should replace both Postgres and Neo4j.
- UUIDs are canonical everywhere, while Markdown filenames remain readable slugs.
- The vault should follow an Obsidian-first style with YAML frontmatter and wiki links.
- Relationship representation should combine frontmatter UUID references for machines with readable wiki links for humans.
- The Karpathy LLM Wiki gist is a relevant conceptual reference. Important ideas to carry forward:
  - Raw sources are immutable.
  - The generated Markdown wiki compounds over time instead of forcing retrieval from scratch every query.
  - A schema/instructions file is the operating contract for the LLM/wiki maintainer.
  - Ingest, query, and lint are distinct workflows.
  - `index.md` and `log.md` are useful navigational and chronological anchors.
  - Obsidian compatibility, YAML frontmatter, graph view, local assets, and git history are practical advantages.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context

- `.planning/PROJECT.md` - Product vision, core value, v1 constraints, and initial decisions.
- `.planning/REQUIREMENTS.md` - Phase 1 requirements KB-01 to KB-05 and OPS-01 to OPS-04.
- `.planning/ROADMAP.md` - Phase 1 goal, success criteria, and phase boundary.
- `.planning/research/SUMMARY.md` - Research implications for Phase 1 and cross-phase risks.
- `.planning/research/ARCHITECTURE.md` - Initial architecture proposal, adjusted by this context for MongoDB replacing Postgres/Neo4j.
- `.planning/research/STACK.md` - Initial stack research, adjusted by this context for React/Vite/Yarn and MongoDB.
- `.planning/research/PITFALLS.md` - Store drift, citation, source, platform, and rating pitfalls.

### External Conceptual Reference

- `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f` - Karpathy LLM Wiki pattern. Use as conceptual guidance for raw sources, generated wiki, schema contract, index/log files, and lint workflow. Do not treat it as an implementation spec.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- No application code exists yet. The repo currently contains planning artifacts, `README.md`, `LICENSE`, and unrelated local IDE/idea files.

### Established Patterns

- GSD planning artifacts live under `.planning/`.
- The repo uses ASCII Markdown planning docs.
- Existing project guide is `AGENTS.md`.

### Integration Points

- Phase 1 will create the first real integration points:
  - `frontend/` React/Vite/Yarn app shell.
  - `backend/` backend skeleton.
  - `vault/` raw/wiki Markdown layout.
  - `infra/` Docker Compose for MongoDB and Qdrant.
  - Shared schema/contracts for UUID identity, Markdown frontmatter, MongoDB records, Qdrant payloads, and relationship records.

</code_context>

<deferred>
## Deferred Ideas

- Strict provider adapter architecture - deferred until integrations stabilize. Phase 1 uses pragmatic direct clients in obvious modules.
- Dedicated graph database - deferred. MongoDB models graph-like relationships for v1 foundation.
- Service dashboard - optional only if planner decides quick local health checks are necessary.
- Real TikTok ingestion, OpenAI calls, paper search, evidence evaluation, ratings, and graph visualization - later phases.

</deferred>

---

*Phase: 01-foundation-and-knowledge-store-contracts*
*Context gathered: 2026-04-18*
