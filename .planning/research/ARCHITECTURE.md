# Architecture Research

**Domain:** AI research fact checking and owned knowledge graph
**Researched:** 2026-04-18
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
Web UI
  URL form
  Report viewer
  Markdown browser
  Search and graph views
      |
      v
API and Job Orchestrator
  Submission API
  Job status API
  Report API
  Knowledge API
      |
      v
Processing Pipeline
  TikTok ingestion adapter
  Transcript and screenshot extraction
  Claim extraction
  Paper discovery
  Paper parsing and summarization
  Evidence evaluation
  Rating update
      |
      v
Owned Knowledge Stores
  Markdown vault
  MongoDB metadata and graph relationships
  Qdrant vector indexes
  Object/file storage for media and PDFs
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Web UI | Submit URLs, inspect reports, browse Markdown, search, inspect graph relationships | Next.js and TypeScript |
| API | Validate submissions, expose job/report/knowledge endpoints | FastAPI |
| Job queue | Run slow ingestion and evaluation work outside request lifecycle | Celery, Dramatiq, or RQ |
| Ingestion adapter | Retrieve public TikTok metadata/video/transcript where compliant | Isolated adapter module |
| Transcript service | Use captions if available or transcribe media | OpenAI transcription or local fallback later |
| Claim extractor | Convert transcript/video context into atomic claims | LLM with structured output |
| Source discovery | Find candidate papers/preprints and disambiguate matches | OpenAI web search plus OpenAlex/Semantic Scholar/arXiv |
| Paper processor | Download or link PDFs, parse text, chunk, summarize | PDF parser plus LLM summarizer |
| Evidence evaluator | Compare claims to source evidence and emit labels | LLM with citation-required structured output |
| Markdown writer | Generate canonical notes and backlinks | File writer with deterministic templates |
| Vector indexer | Embed and index source chunks and notes | Qdrant |
| Graph writer | Create entities and relationships | MongoDB relationship collections |
| Rating engine | Update transparent rating snapshots from evidence history | Deterministic rules plus audit trail |

## Recommended Project Structure

```
backend/
  app/
    api/                 # HTTP routes
    jobs/                # Queue tasks and orchestration
    ingestion/           # TikTok adapter and transcript/media extraction
    claims/              # Claim extraction schemas and prompts
    sources/             # Paper search, source ranking, downloads
    papers/              # PDF parsing, chunking, paper summaries
    evaluation/          # Evidence labels and report generation
    knowledge/           # Markdown, MongoDB, Qdrant writers
    ratings/             # Creator/source/paper/author scoring
    settings/            # Config, secrets, provider adapters
  tests/
frontend/
  app/
    submit/              # URL submission flow
    jobs/                # Job status
    reports/             # Fact-check report viewer
    knowledge/           # Markdown browser
    graph/               # Graph view
    search/              # Vector and keyword search
  components/
vault/
  videos/
  creators/
  claims/
  papers/
  authors/
  sources/
  reports/
infra/
  docker-compose.yml
  migrations/
```

### Structure Rationale

- **backend/app/knowledge:** Keeps Markdown, vector, and graph writes coordinated.
- **backend/app/ingestion:** Keeps platform-specific and compliance-sensitive code isolated.
- **backend/app/sources:** Separates paper discovery from evidence evaluation so source ranking can improve independently.
- **vault/:** Makes the owned Markdown corpus visible and portable from the start.
- **infra/:** Local service setup is central because the product depends on multiple stores.

## Architectural Patterns

### Pattern 1: Adapter Boundary for External Providers

**What:** Wrap OpenAI, TikTok, paper indexes, MongoDB, and Qdrant behind narrow interfaces.
**When to use:** Always for third-party APIs and platform-specific ingestion.
**Trade-offs:** Slightly more code up front, but prevents vendor lock-in and makes tests reliable.

### Pattern 2: Canonical Markdown plus Derived Indexes

**What:** Treat Markdown notes and MongoDB structured records as durable knowledge; Qdrant is an index/view over that knowledge.
**When to use:** For notes, reports, paper summaries, and source records.
**Trade-offs:** Requires consistency checks between Markdown, MongoDB documents/relationships, and vector indexes.

### Pattern 3: Claim-Level Evaluation

**What:** Extract atomic claims, evaluate each independently, and aggregate at report level.
**When to use:** Every fact-check report.
**Trade-offs:** More processing cost than a single summary verdict, but much more auditable.

## Data Flow

### Request Flow

```
User submits TikTok URL
    |
FastAPI validates URL and creates job
    |
Queue worker retrieves video metadata/transcript/media
    |
Claim extractor creates timestamped claims
    |
Source discovery finds papers/preprints
    |
Paper processor creates summaries and chunks
    |
Evidence evaluator labels each claim
    |
Markdown writer creates notes and report
    |
MongoDB relationship records and Qdrant indexes are updated
    |
UI displays report, notes, search, and graph relationships
```

### Key Data Flows

1. **Video to claims:** TikTok URL -> media/transcript -> transcript chunks -> structured claims with timestamps.
2. **Claims to sources:** Claim text and context -> web/paper-index search -> candidate papers -> ranked evidence.
3. **Sources to knowledge:** Paper metadata/PDF -> chunks -> summary Markdown -> vector index -> graph entities.
4. **Evidence to report:** Claims plus evidence chunks -> labels -> report Markdown -> UI.
5. **Report to ratings:** Labeled claims and source quality -> transparent rating records.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Prototype | Single backend worker, local MongoDB/Qdrant, filesystem vault. |
| Small team | Dedicated worker pool, object storage for media/PDFs, scheduled consistency checks. |
| Company deployment | Tenant isolation, audit logs, queue partitioning, configurable provider adapters, backup/export workflow. |

### Scaling Priorities

1. **First bottleneck:** LLM and web-search cost/latency. Fix with caching, source reuse, and job batching.
2. **Second bottleneck:** PDF parsing and embedding. Fix with chunk-level deduplication and background indexing.
3. **Third bottleneck:** Graph quality. Fix with entity normalization and correction workflows before adding graph algorithms.

## Anti-Patterns

### Anti-Pattern 1: Verdict-First Fact Checking

**What people do:** Ask an LLM whether the video is true and display the answer.
**Why it is wrong:** It hides claim boundaries, source quality, and uncertainty.
**Do this instead:** Extract claims, retrieve evidence, and label each claim with citations.

### Anti-Pattern 2: Indexes as Source of Truth

**What people do:** Store only vectors or graph nodes and treat them as canonical.
**Why it is wrong:** Users cannot audit or move their knowledge easily.
**Do this instead:** Store Markdown and structured metadata canonically; rebuild indexes from them.

### Anti-Pattern 3: Unbounded Platform Scraping

**What people do:** Add downloader calls directly wherever a video is needed.
**Why it is wrong:** It creates compliance, maintenance, and reliability risk.
**Do this instead:** Use a single ingestion adapter with explicit allowed source types and documented behavior.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI Responses API | Provider adapter | Use web search with citation requirements; do not store durable knowledge only in OpenAI. |
| TikTok | Ingestion adapter | Prefer official metadata APIs where possible; downloading needs compliance review. |
| OpenAlex | Paper-search adapter | Good for broad work metadata and search. |
| Semantic Scholar | Paper-search adapter | Useful for citation, author, recommendation, and embedding metadata. |
| arXiv | Paper-search adapter | Useful for AI preprints. |
| Qdrant | Repository/index adapter | Store chunk vectors with payload filters for source, paper, claim, and note IDs. |
| MongoDB | Metadata and graph repository | Store jobs, reports, entity documents, rating snapshots, and explicit relationship edges. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| API to jobs | Queue message | Request should return quickly with job ID. |
| Jobs to knowledge stores | Service methods | Writes should be idempotent by stable source IDs. |
| Markdown to indexes | Event or explicit reindex step | Needed to prevent drift. |
| Evaluation to ratings | Structured records | Ratings must be reproducible from evidence history. |

## Sources

- https://platform.openai.com/docs/guides/tools-web-search - web search, citations, domain filtering, and live access.
- https://qdrant.tech/documentation/search/ - vector search, filters, hybrid queries, text search.
- https://www.mongodb.com/docs/ - document database, aggregation, indexes, and relationship modeling.
- https://developers.tiktok.com/doc/display-api-overview/ - official TikTok API boundaries for public video metadata.
- https://docs.openalex.org/api-entities/works/search-works - paper search API.
- https://www.semanticscholar.org/product/api - academic graph API.

---
*Architecture research for: AI research fact checker*
*Researched: 2026-04-18*
