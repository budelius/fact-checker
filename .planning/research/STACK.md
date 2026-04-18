# Stack Research

**Domain:** AI research fact checking, video ingestion, Markdown knowledge base, vector retrieval, and knowledge graph
**Researched:** 2026-04-18
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | Latest stable supported by dependencies | Backend, ingestion, transcription, paper processing, LLM orchestration | Best ecosystem fit for media processing, PDF parsing, embeddings, vector DB clients, and graph tooling. |
| FastAPI | Latest stable | HTTP API and async job endpoints | Fits Python services, background task orchestration, typed request/response contracts, and frontend API integration. |
| Next.js + TypeScript | Latest stable | Website, report UI, Markdown browser, graph/search UI | Strong fit for interactive web UI, server/client rendering boundaries, and typed frontend code. |
| MongoDB | Latest stable | Durable job metadata, structured entity documents, reports, source records, rating snapshots, and graph relationship edges | Replaces separate Postgres and Neo4j services for v1, reducing local infrastructure while keeping structured metadata and relationship records outside the Markdown vault. |
| Markdown vault | Plain files | Canonical user-owned knowledge store | Portable, inspectable, Obsidian-compatible, and easy to version or export. |
| Qdrant | Latest stable | Vector and hybrid search over papers, notes, claims, and transcripts | Official docs cover vector search, filtering, sparse vectors, hybrid queries, full-text search, and relevance tuning. |
| OpenAI Responses API | Current API | Claim extraction, evidence comparison, web search, summarization, optional transcription | Official docs support web search and file search tools; live web search can return cited results. |

### Supporting Libraries and Services

| Library or Service | Version | Purpose | When to Use |
|--------------------|---------|---------|-------------|
| OpenAlex API | Current public API | Search works by title, abstract, and full text where available | Paper discovery and metadata lookup. |
| Semantic Scholar API | Current public API | Paper, author, citation, recommendation, and embedding metadata | Paper disambiguation and related paper discovery. |
| arXiv API | Current public API | Preprint lookup and metadata | AI research preprint ground truth. |
| yt-dlp | Latest stable, compliance-gated | Public video retrieval adapter | Only after platform-terms review; keep replaceable. |
| PyMuPDF or equivalent | Latest stable | PDF text extraction | Parse downloaded papers for chunking and Markdown summaries. |
| Celery, Dramatiq, or RQ | Latest stable | Background jobs | Use for long-running ingestion, transcription, paper search, and evaluation jobs. |
| Docker Compose | Current | Local services | Run MongoDB, Qdrant, and app services consistently in development. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Ruff | Python lint/format | Fast default for Python code quality. |
| Pytest | Backend tests | Required for ingestion adapters, source ranking, and evaluation labels. |
| Playwright | UI and integration tests | Validate URL submission, report rendering, Markdown viewer, and graph/search interactions. |
| TypeScript strict mode | Frontend correctness | Helps stabilize report and entity schemas. |

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Qdrant | OpenAI file search | Use OpenAI file search for a quick hosted prototype; keep Qdrant for owned retrieval and portability. |
| Qdrant | pgvector | Use pgvector if operational simplicity beats retrieval features. |
| MongoDB relationship collections | Neo4j or Memgraph | Use a dedicated graph database later if relationship traversal, graph algorithms, or visualization requirements outgrow document/edge collections. |
| MongoDB operational documents | PostgreSQL | Use relational tables if strict relational constraints, SQL reporting, or transactional joins become the dominant requirements. |
| FastAPI | Django | Use Django if admin UI, auth, and ORM conventions become the highest priority. |
| Next.js | Plain server-rendered templates | Use templates if the UI stays minimal and graph/Markdown browsing is postponed. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LLM memory as the durable knowledge store | Locks knowledge into a vendor and weakens auditability. | Markdown vault plus MongoDB and Qdrant. |
| A single undifferentiated "truth score" | Hides uncertainty and overstates conclusions. | Claim-level evidence labels with citations. |
| Direct platform-specific scraping spread through the codebase | Breaks when platform markup changes and makes compliance hard to audit. | A narrow ingestion adapter with terms checks and replaceable implementations. |
| Paper summaries without links to source text | Creates unverifiable derived knowledge. | Markdown summaries with DOI/arXiv/OpenAlex/Semantic Scholar links and evidence chunks. |

## Stack Patterns by Variant

**If local-first or EU-controlled deployment becomes mandatory:**
- Keep Markdown, MongoDB, and Qdrant self-hosted.
- Add provider adapters for LLM and transcription services.
- Evaluate local transcription and local embedding models during a later milestone.

**If the MVP needs to move quickly:**
- Start with FastAPI, Next.js, MongoDB, Qdrant, and OpenAI APIs.
- Keep all third-party integrations behind adapters so they can be replaced.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| FastAPI | Python latest stable | Verify current Python support before installation. |
| Qdrant client | Qdrant server | Pin client and server versions together in Docker Compose. |
| MongoDB Python driver | MongoDB server | Pin driver and server versions together in Docker Compose. |
| OpenAI SDK | Responses API | Verify current SDK method names when implementing. |

## Sources

- https://platform.openai.com/docs/guides/tools-web-search - OpenAI Responses API web search, citations, domain filtering, and live web access.
- https://platform.openai.com/docs/guides/tools-file-search - OpenAI hosted file search and vector stores.
- https://qdrant.tech/documentation/search/ - Qdrant search, filtering, hybrid queries, text search, and relevance features.
- https://www.mongodb.com/docs/ - MongoDB document database, aggregation, indexes, and developer tooling documentation.
- https://developers.tiktok.com/doc/display-api-overview/ - TikTok Display API scope and public video metadata constraints.
- https://docs.openalex.org/api-entities/works/search-works - OpenAlex work search across titles, abstracts, and full text where available.
- https://www.semanticscholar.org/product/api - Semantic Scholar Academic Graph API capabilities.

---
*Stack research for: AI research fact checker*
*Researched: 2026-04-18*
