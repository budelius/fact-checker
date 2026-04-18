# Project Research Summary

**Project:** Fact Checker
**Domain:** AI research fact checking, owned Markdown knowledge base, vector retrieval, and knowledge graph
**Researched:** 2026-04-18
**Confidence:** MEDIUM

## Executive Summary

This product should be built as a claim-level evidence pipeline, not as a single chatbot answer. The durable value is the owned knowledge base: Markdown notes are the canonical user-facing memory, while Qdrant and Neo4j provide retrieval and relationship views over the same evidence.

The recommended v1 is an end-to-end thin slice: public TikTok URL submission, transcript extraction, claim extraction, paper/preprint discovery, paper Markdown summaries, claim-level evidence labels, vector indexing, graph writes, and a web UI for reports and Markdown browsing. This is broad, but it validates the unique product thesis: every fact check improves a reusable, user-owned knowledge graph.

The highest risks are wrong paper matching, hallucinated citations, social-platform ingestion fragility, and opaque reputation scores. The roadmap should front-load storage/schema boundaries and compliance-safe ingestion, then make citation-grounded evaluation and consistency checks explicit success criteria.

## Key Findings

### Recommended Stack

Use a Python/FastAPI backend, Next.js/TypeScript frontend, Postgres for operational metadata, Markdown files as the canonical knowledge vault, Qdrant for vector/hybrid search, and Neo4j as the first graph database. Use OpenAI Responses API for live web search, extraction, summarization, and comparison, but keep durable knowledge outside OpenAI-hosted memory.

**Core technologies:**
- Python/FastAPI: backend and long-running AI/data pipeline.
- Next.js/TypeScript: URL submission, report viewer, Markdown browser, graph/search UI.
- Markdown vault: portable, inspectable source of owned knowledge.
- Qdrant: vector and hybrid retrieval over papers, notes, claims, and transcripts.
- Neo4j: graph relationships and source trails across creators, claims, papers, authors, sources, and evidence.
- Postgres: jobs, reports, source metadata, and rating snapshots.
- OpenAI Responses API: web search with citations and structured reasoning steps.

### Expected Features

**Must have (table stakes):**
- Public TikTok URL submission and job status.
- Transcript extraction or transcription fallback.
- Claim extraction with timestamp/source context.
- Paper/preprint discovery across live web and academic indexes.
- Paper metadata, PDF/link handling, chunking, and Markdown summaries.
- Claim-level labels: supported, contradicted, mixed, insufficient evidence.
- Markdown vault generation and browsing.
- Qdrant indexing and Neo4j graph writes.

**Should have (competitive):**
- Source disambiguation from creator references and screenshots.
- Transparent creator/paper/author/source rating history.
- Search and graph views that improve future checks.
- User-owned exportable corpus.

**Defer (v2+):**
- Instagram ingestion.
- Chat client and OpenClaw integration.
- Meta Ray-Ban or other smart-glasses streaming use cases.
- Real-time meeting assistant.
- News as a first-class ground-truth tier.

### Architecture Approach

The system should be a job-oriented pipeline with clear adapters. User requests create jobs; workers run TikTok ingestion, transcript processing, claim extraction, source discovery, paper processing, evidence evaluation, Markdown writing, vector indexing, graph writes, and rating updates. Markdown is canonical; Postgres tracks operational records; Qdrant and Neo4j are query/index layers with consistency checks.

**Major components:**
1. Web UI - URL submission, report viewer, Markdown browser, search, graph.
2. API and job orchestrator - validation, job status, report and knowledge endpoints.
3. Ingestion adapter - platform-specific TikTok work isolated behind a compliance boundary.
4. Claim/source/paper/evaluation pipeline - transforms media into evidence-backed labels.
5. Knowledge stores - Markdown vault, Postgres, Qdrant, Neo4j, media/PDF storage.
6. Rating engine - transparent evidence-history scoring for creators, papers, authors, and sources.

### Critical Pitfalls

1. **Hallucinated or weak citations** - reject labels without stored source evidence.
2. **Wrong paper matching** - record candidate source ranking and matching rationale.
3. **Treating preprints as final truth** - track source type, venue/status, dates, limitations, and confidence separately.
4. **Knowledge store drift** - use stable IDs and consistency checks across Markdown, Postgres, Qdrant, and Neo4j.
5. **Platform ingestion risk** - isolate TikTok code and add fallback fixtures/transcript paths.
6. **Opaque ratings** - ratings must show evidence count, inputs, and confidence.

## Implications for Roadmap

### Phase 1: Foundation and Knowledge Store Contracts

**Rationale:** The rest of the project depends on stable IDs, Markdown conventions, and store boundaries.
**Delivers:** App skeleton, config, schemas, local services, Markdown vault templates, store adapters.
**Addresses:** Knowledge ownership, Qdrant, Neo4j, Postgres, provider adapters.
**Avoids:** Knowledge store drift and vendor lock-in.

### Phase 2: TikTok Ingestion and Claim Extraction

**Rationale:** The product starts from public creator video links.
**Delivers:** URL submission, job status, TikTok ingestion adapter, transcript fallback, screenshots/keyframes, claim extraction.
**Addresses:** First user workflow.
**Avoids:** Platform-specific code spread through the app.

### Phase 3: Ground-Truth Discovery and Paper Processing

**Rationale:** Fact checking is only useful if the system finds the right papers.
**Delivers:** Live web search, OpenAlex/Semantic Scholar/arXiv adapters, source ranking, paper metadata, PDF/link handling, Markdown paper summaries.
**Uses:** OpenAI web search, paper APIs, PDF parser, Markdown writer, Qdrant chunks.

### Phase 4: Evidence Evaluation and Fact-Check Reports

**Rationale:** Claim labels are the visible fact-checking value.
**Delivers:** Claim-to-evidence comparison, evidence labels, uncertainty explanations, cited reports, report UI.
**Avoids:** Hallucinated citations and verdict-first fact checking.

### Phase 5: Knowledge Browser, Search, Graph, and Ratings

**Rationale:** The strategic value is cumulative knowledge and future improvement.
**Delivers:** Obsidian-like Markdown browser, search UI, graph UI, entity pages, basic transparent ratings, consistency checks.
**Implements:** Owned knowledge graph and reusable fact-checking memory.

### Phase Ordering Rationale

- Stable storage contracts come first because every downstream artifact writes into Markdown, vector, graph, and metadata stores.
- Ingestion and claims come before paper search because the source-discovery query depends on extracted claims and video context.
- Paper processing comes before evaluation because labels must cite stored evidence chunks.
- Ratings wait until reports and graph relationships exist because ratings need evidence history.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** TikTok ingestion compliance and technical reliability.
- **Phase 3:** Paper disambiguation and PDF parsing quality.
- **Phase 4:** Prompt/evaluation rubric design for claim labels.
- **Phase 5:** Rating model, graph schema, and graph visualization.

Phases with standard patterns:
- **Phase 1:** FastAPI, Next.js, Postgres, Qdrant, Neo4j, Docker Compose patterns are well documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core choices are defensible, but exact versions must be verified during phase planning. |
| Features | HIGH | Derived directly from user goals and v1 choices. |
| Architecture | MEDIUM | Pipeline shape is clear; graph/rating details need deeper design. |
| Pitfalls | MEDIUM | Main risks are known; platform compliance needs phase-specific verification. |

**Overall confidence:** MEDIUM

### Gaps to Address

- **TikTok ingestion legality and reliability:** Phase 2 must document allowed approach and fallback paths.
- **Graph database finalization:** Neo4j is the default target, but Phase 1 should verify deployment fit.
- **Rating rubric:** Phase 5 must define transparent, non-punitive scoring rules and confidence thresholds.
- **Model/provider abstraction:** Phase 1 should keep OpenAI calls behind adapters to reduce lock-in.

## Sources

### Primary (HIGH confidence)

- https://platform.openai.com/docs/guides/tools-web-search - web search, citations, domain filtering, live access.
- https://platform.openai.com/docs/guides/tools-file-search - hosted file search and vector stores.
- https://qdrant.tech/documentation/search/ - vector, filtering, hybrid, and text search capabilities.
- https://neo4j.com/docs/ - graph database, Cypher, graph tooling, and graph data science.
- https://developers.tiktok.com/doc/display-api-overview/ - official public video metadata API boundaries.
- https://docs.openalex.org/api-entities/works/search-works - work search capabilities.
- https://www.semanticscholar.org/product/api - academic graph API capabilities.

### Secondary (MEDIUM confidence)

- User project brief from 2026-04-18 - product goals, v1 choices, and constraints.

---
*Research completed: 2026-04-18*
*Ready for roadmap: yes*
