# Phase 1: Foundation and Knowledge Store Contracts - Research

**Researched:** 2026-04-18
**Domain:** monorepo foundation, React/Vite frontend shell, FastAPI backend skeleton, MongoDB/Qdrant local services, Obsidian-first Markdown vault
**Confidence:** HIGH for scaffold/tooling basics, MEDIUM for MongoDB-as-graph modeling details

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Use a monorepo.
- Use `frontend/` for the web app.
- Use React, TypeScript, Vite, and Yarn for the frontend.
- Use `backend/` for the backend service; Python/FastAPI remains the assumed stack.
- Use `vault/` for the owned Markdown knowledge base.
- Use `infra/` for Docker Compose, service configuration, migrations, and local infrastructure files.
- Keep Docker Compose simple in Phase 1. Default Compose should run datastores only; backend/frontend run on the host.
- Use MongoDB as the primary app metadata database.
- MongoDB replaces both Postgres and Neo4j for v1 foundation.
- Qdrant remains the vector database target.
- Dedicated graph database work is deferred. Model graph-like relationships in MongoDB first.
- Use UUIDs everywhere for canonical entity identity.
- Markdown files use readable slugs; UUIDs live in YAML frontmatter.
- Optimize the vault for Obsidian-first use with YAML frontmatter and wiki links.
- Relationships are represented with both frontmatter UUID references and readable wiki links in the body.
- Apply Karpathy's LLM Wiki pattern where useful: raw sources, generated wiki, schema/maintenance instructions, `index.md`, `log.md`, and future linting.
- Use pragmatic direct clients first, but keep external calls in obvious modules.
- Phase 1 UI is a React/Vite knowledge-browser shell only.

### the agent's Discretion

- Exact Docker Compose organization and service names.
- Backend project tooling, as long as it fits Python/FastAPI.
- MongoDB collection names, as long as UUID identity and relationship contracts are clear.
- Qdrant collection names, as long as payloads include UUID/entity metadata and trace back to canonical notes/source records.
- Visual styling details inside the approved UI-SPEC contract.

### Deferred Ideas (OUT OF SCOPE)

- Strict provider adapter architecture.
- Dedicated graph database.
- Real TikTok ingestion, OpenAI calls, paper search, evidence evaluation, ratings, and graph visualization.
- Service dashboard, unless it is necessary for local health checks.
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Local datastore services | Infrastructure | Backend | Docker Compose owns MongoDB and Qdrant startup; backend consumes connection strings. |
| UUID/entity contract | Backend | Vault, Qdrant, MongoDB | Backend schemas should define canonical fields that all stores share. |
| Markdown vault structure | Storage | Frontend | Vault files are canonical human-readable knowledge; frontend shell previews the same entity model. |
| MongoDB relationship storage | Database/Storage | Backend | MongoDB stores entity docs and relationship edge docs for v1. |
| Qdrant vector payload contract | Database/Storage | Backend | Qdrant points need payload fields that trace to UUIDs, entity types, and vault paths. |
| Knowledge browser shell | Browser/Client | Static files | React/Vite renders static placeholder sections in Phase 1. |
| Secrets and untrusted input guardrails | Backend | Infrastructure | Config and docs must define env handling and prompt-input boundaries before real external content. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 1 should create a thin but concrete foundation: local datastores in Compose, backend schemas/repository boundaries, an Obsidian-first vault skeleton, and a React/Vite frontend shell that reflects the vault entity model. The key implementation risk is not algorithmic complexity; it is contract drift across Markdown, MongoDB, and Qdrant. The plan should therefore prioritize stable UUID fields, deterministic vault paths, relationship documents, and payload conventions.

Current official docs support the chosen stack. Vite's official guide supports React TypeScript scaffolding via `yarn create vite frontend --template react-ts` and notes that current Vite requires Node.js 20.19+ or 22.12+. React docs recommend TypeScript type packages for React projects and Strict Mode for finding component bugs early. MongoDB's Docker docs recommend the official MongoDB Community image for development/testing, while Qdrant's docs provide official Docker and Compose patterns with persistent storage under `/qdrant/storage`.

**Primary recommendation:** Plan Phase 1 as five focused plans: infrastructure, backend contracts, vault schema/templates, frontend shell, and cross-store consistency/docs.
</research_summary>

<standard_stack>
## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| React | latest stable | Frontend UI | Current standard for component-based web apps; UI-SPEC calls for React. |
| TypeScript | latest stable | Frontend typing | Required by user; React docs support TypeScript with React type packages. |
| Vite | latest stable | Frontend dev/build tool | Official Vite guide supports React TypeScript template and Yarn scaffolding. |
| Yarn | latest stable | Frontend package manager | Explicit user choice. |
| Python | 3.12+ recommended | Backend runtime | Stable modern Python target for FastAPI and current tooling. |
| FastAPI | latest stable | Backend HTTP API skeleton | Fits typed API and health/contract endpoints. |
| Pydantic v2 + pydantic-settings | latest stable | Backend schemas/settings | Canonical Python schema/config layer for FastAPI projects. |
| MongoDB Community Docker image | latest stable | Metadata and relationship store | User selected MongoDB; official MongoDB Docker image is maintained by MongoDB for dev/test. |
| PyMongo | latest stable | MongoDB Python client | Official Python driver. Async PyMongo exists but should be verified during implementation if used. |
| Qdrant Docker image | latest stable | Vector store | Official docs provide Docker and Docker Compose patterns. |
| qdrant-client | latest stable | Qdrant Python client | Official Python client for collection and point operations. |
| uv | latest stable | Backend project/dependency manager | Fast Python package/project manager with lockfiles and reproducible commands. |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| Ruff | latest stable | Python lint/format | Baseline backend quality. |
| Pytest | latest stable | Backend tests | Schema, config, repository, and contract tests. |
| Vitest | latest stable | Frontend unit tests | Static UI component and data contract tests. |
| lucide-react | latest stable | UI icons | Approved by UI-SPEC for navigation icons. |
| Docker Compose | current v2 | Local datastores | Run MongoDB and Qdrant only by default. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MongoDB relationship docs | Neo4j | Neo4j is stronger for graph traversal but explicitly deferred. |
| uv | Poetry | Poetry is mature; uv is faster and simple for a new app skeleton. |
| Vite | Next.js | Next.js was an initial research default, but user locked React/Vite/Yarn. |
| Strict adapters | Direct clients in modules | Strict adapters reduce lock-in, but user chose pragmatic direct clients first. |

**Installation examples for implementation planning:**

```bash
yarn create vite frontend --template react-ts
cd frontend && yarn add lucide-react && yarn add -D vitest @testing-library/react @testing-library/jest-dom

uv init backend --bare
cd backend && uv add fastapi uvicorn pydantic pydantic-settings pymongo qdrant-client python-frontmatter pyyaml
cd backend && uv add --dev pytest ruff httpx
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### System Architecture Diagram

```text
Developer
  |
  | docker compose up -d
  v
MongoDB + Qdrant

Developer
  |
  | uv run / yarn dev
  v
Backend skeleton <-----> MongoDB collections
       |                         |
       |                         v
       |                  relationship edge docs
       |
       +---------------> Qdrant collections
       |
       +---------------> vault/ Markdown schema/templates

Frontend shell
  |
  v
Static knowledge browser placeholder
  |
  v
Entity sections mirror vault/wiki folders
```

### Recommended Project Structure

```text
backend/
  app/
    main.py
    settings.py
    schemas/
      entities.py
      relationships.py
      vector_payloads.py
    repositories/
      mongo.py
      qdrant.py
    safety/
      input_boundaries.py
  tests/
    test_schemas.py
    test_settings.py
    test_repository_contracts.py
frontend/
  package.json
  vite.config.ts
  src/
    App.tsx
    main.tsx
    data/sampleVault.ts
    components/
      AppShell.tsx
      VaultNavigation.tsx
      NotePreview.tsx
      MetadataPanel.tsx
    styles/
      tokens.css
      app.css
vault/
  raw/
    videos/
    papers/
    images/
    transcripts/
  wiki/
    videos/
    creators/
    claims/
    papers/
    authors/
    sources/
    evidence/
    reports/
    topics/
  templates/
  index.md
  log.md
  SCHEMA.md
infra/
  docker-compose.yml
  README.md
.env.example
```

### Pattern 1: Canonical UUID + External Aliases

**What:** Each entity document/note has `uuid` as canonical identity. External source IDs are stored in `external_ids` or `aliases`.
**When to use:** All MongoDB docs, Markdown frontmatter, Qdrant payloads, and relationship edge docs.

### Pattern 2: Relationship Documents in MongoDB

**What:** Store explicit relationship edge documents such as `{ uuid, type, source_uuid, target_uuid, provenance, created_at }`.
**When to use:** For graph-like relationships until a dedicated graph DB is justified.

### Pattern 3: Markdown Frontmatter + Wiki Body Links

**What:** Store machine-readable UUID references in YAML frontmatter and human-readable `[[wiki-links]]` in body text.
**When to use:** Every generated wiki note.

### Anti-Patterns to Avoid

- **Slug as identity:** Slugs can change and collide. UUID is canonical.
- **Vectors as source of truth:** Qdrant points are derived query artifacts, not canonical knowledge.
- **Scattered SDK calls:** Direct clients are allowed only in obvious repository/service modules.
- **Pretending placeholder UI is live:** Phase 1 UI must not imply ingestion, search, graph, or reports work.
- **Storing secrets in docs/vault/logs:** Secrets stay in env/config only.
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML frontmatter parsing | Regex parser | `python-frontmatter` or YAML library | Frontmatter edge cases are easy to mishandle. |
| UUID validation | Custom string checks | Python `uuid.UUID`, Pydantic UUID types | Standard parsing catches invalid IDs. |
| MongoDB client lifecycle | Ad-hoc global socket handling | Repository module with explicit client factory | Easier to test and close connections. |
| Qdrant HTTP calls | Raw requests | `qdrant-client` | Official client tracks API shape. |
| Vite scaffold | Manual bundler config | `yarn create vite frontend --template react-ts` | Official template avoids stale setup. |
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Store Drift from Day One

**What goes wrong:** Markdown, MongoDB, and Qdrant use different IDs or missing payload links.
**Why it happens:** Each layer is implemented independently without shared schema contracts.
**How to avoid:** Define entity, relationship, frontmatter, and Qdrant payload schemas before building integrations.
**Warning signs:** Qdrant payload lacks `uuid` or `vault_path`; MongoDB docs store slug as `_id`; Markdown lacks frontmatter UUID.

### Pitfall 2: UI Overpromises Later Capabilities

**What goes wrong:** Phase 1 shell shows URL submission or live search that does not exist.
**Why it happens:** It is tempting to make the shell feel complete.
**How to avoid:** Keep UI to static vault navigation, placeholder notes, metadata, and relationship previews.
**Warning signs:** Buttons labeled "Fact check video", "Search", or "Generate report" appear in Phase 1.

### Pitfall 3: MongoDB Relationship Model Becomes Implicit

**What goes wrong:** Relationship data is scattered as nested arrays on many entity docs and cannot be queried consistently.
**Why it happens:** Without Neo4j, developers may skip an explicit edge model.
**How to avoid:** Define `relationships` documents with source UUID, target UUID, type, provenance, and timestamps.
**Warning signs:** There is no dedicated relationship schema or collection.

### Pitfall 4: Compose Tries to Run Everything

**What goes wrong:** Local setup becomes heavy before the app exists.
**Why it happens:** Full-stack Compose is convenient but premature.
**How to avoid:** Default Compose runs MongoDB and Qdrant only, matching the context decision.
**Warning signs:** Compose requires frontend/backend images in Phase 1.
</common_pitfalls>

<code_examples>
## Code Examples

Verified patterns from official sources:

### Vite React TypeScript scaffolding

```bash
# Source: https://vite.dev/guide/
yarn create vite frontend --template react-ts
```

### React Strict Mode root

```tsx
// Source: https://react.dev/reference/react/StrictMode
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

### MongoDB Community Docker

```bash
# Source: https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-community-with-docker/
docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
```

### Qdrant local Docker

```bash
# Source: https://qdrant.tech/documentation/quick-start/
docker run -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
  qdrant/qdrant
```
</code_examples>

<sota_updates>
## State of the Art (2024-2026)

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Next.js by default for any React app | Vite for lightweight app shells | User decision, current Vite docs | Keep Phase 1 fast and client-side. |
| Separate Postgres + Neo4j services | MongoDB for metadata and relationship docs | User decision | Simpler local infrastructure; requires explicit edge schema. |
| Heavy provider abstraction first | Direct clients in obvious modules | User decision | Speeds MVP but plans must keep calls contained. |
| UUID in filenames | UUID in frontmatter, slug filenames | User decision | Human-readable vault with explicit collision handling. |

**New tools/patterns to consider:**

- uv for Python project and lockfile management.
- React Strict Mode for early component bug detection.
- Qdrant payload filters for tracing vector points back to UUIDs and vault paths.

**Deprecated/outdated:**

- Vite docs for older major versions have different Node requirements. Use current Vite docs when implementing.
- Treating MongoDB documents with nested arrays as a complete graph replacement is risky; explicit relationship docs are safer.
</sota_updates>

<open_questions>
## Open Questions

1. **Should backend use async PyMongo or synchronous PyMongo in Phase 1?**
   - What we know: PyMongo has async API documentation, but some docs describe async as newer/beta in prior versions.
   - What's unclear: Which driver shape will be most stable at implementation time.
   - Recommendation: For Phase 1, planner can use synchronous PyMongo inside simple repository functions unless official current docs confirm async stability during execution.

2. **Should Qdrant collections be created in Phase 1 or only described?**
   - What we know: Phase 1 success criteria say boundaries can write/read test entities without later ingestion.
   - What's unclear: Whether execution environment will have Docker/network dependencies ready.
   - Recommendation: Include contract code/tests that can run in unit mode without live Qdrant, plus optional integration checks when Qdrant is available.
</open_questions>

<sources>
## Sources

### Primary (HIGH confidence)

- https://vite.dev/guide/ - Vite React TypeScript scaffolding, Yarn command, current Node compatibility note.
- https://react.dev/learn/typescript - React TypeScript type setup.
- https://react.dev/reference/react/StrictMode - Strict Mode development checks.
- https://docs.astral.sh/uv/ - uv project/dependency manager.
- https://docs.astral.sh/uv/guides/projects/ - uv project files and lockfile behavior.
- https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-community-with-docker/ - MongoDB official Docker image for development/testing.
- https://qdrant.tech/documentation/quick-start/ - Qdrant local Docker run command and ports.
- https://qdrant.tech/documentation/guides/ - Qdrant Docker Compose example and persistent storage guidance.

### Secondary (MEDIUM confidence)

- https://pymongo.readthedocs.io/en/latest/api/pymongo/asynchronous/ - PyMongo async API docs, verify exact stability before committing to async.

### Tertiary (LOW confidence - needs validation)

- None.
</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: React/Vite/Yarn, Python/FastAPI, MongoDB, Qdrant, Markdown vault.
- Ecosystem: uv, PyMongo, qdrant-client, Pydantic, Vitest, Ruff, Pytest.
- Patterns: monorepo layout, UUID-first identity, MongoDB relationship edges, Obsidian-first Markdown.
- Pitfalls: store drift, placeholder UI overclaiming, implicit graph modeling, over-heavy Compose.

**Confidence breakdown:**
- Standard stack: HIGH - grounded in official docs and locked user choices.
- Architecture: MEDIUM - clear for MVP, but MongoDB graph modeling needs validation in later phases.
- Pitfalls: HIGH - directly tied to phase context and project research.
- Code examples: HIGH - copied from official docs patterns in abbreviated form.

**Research date:** 2026-04-18
**Valid until:** 2026-05-18 for stable tool choices; verify Vite/Node requirements and PyMongo async status during execution.
</metadata>

---

*Phase: 01-foundation-and-knowledge-store-contracts*
*Research completed: 2026-04-18*
*Ready for planning: yes*
