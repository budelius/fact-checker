# Roadmap: Fact Checker

**Created:** 2026-04-18
**Granularity:** Coarse
**Core Value:** Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## Overview

| Phase | Name | Goal | Requirements |
|-------|------|------|--------------|
| 1 | Foundation and Knowledge Store Contracts | Establish the app skeleton, storage contracts, provider boundaries, and owned knowledge model that every later phase writes into. | KB-01, KB-02, KB-03, KB-04, KB-05, OPS-01, OPS-02, OPS-03, OPS-04 |
| 2 | TikTok Ingestion and Claim Extraction | Let a user submit a public TikTok URL or upload a video and turn the content into timestamped AI research claims with transcript and visual context. | ING-01, ING-02, ING-03, ING-04, ING-05, CLM-01, CLM-02, CLM-03, UI-01 |
| 3 | Ground-Truth Discovery and Paper Processing | Find the right papers/preprints, process them into reusable evidence, and store paper knowledge as Markdown plus indexed chunks. | SRC-01, SRC-02, SRC-03, SRC-04, SRC-05, PPR-01, PPR-02, PPR-03, PPR-04, PPR-05 |
| 4 | Evidence Evaluation and Fact-Check Reports | Compare each video claim against stored source evidence and produce cited, uncertainty-aware fact-check reports. | EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, UI-02 |
| 5 | Knowledge Browser, Search, Graph, and Ratings | Make the accumulated Markdown/vector/graph knowledge useful for future checks through browsing, search, graph inspection, consistency checks, and transparent ratings. | KB-06, UI-03, UI-04, UI-05, RAT-01, RAT-02, RAT-03 |

**Coverage:** 41 of 41 v1 requirements mapped.

## Phase Details

### Phase 1: Foundation and Knowledge Store Contracts

**Status:** Complete (verified 2026-04-18)

**Goal:** Establish the app skeleton, storage contracts, provider boundaries, and owned knowledge model that every later phase writes into.

**Requirements:** KB-01, KB-02, KB-03, KB-04, KB-05, OPS-01, OPS-02, OPS-03, OPS-04

**UI hint:** yes

**Success Criteria:**

1. Local development can start the backend, frontend shell, MongoDB, and Qdrant.
2. The project has stable entity schemas for videos, creators, claims, papers, authors, sources, evidence, reports, and ratings.
3. Markdown note templates exist for every canonical entity type and use stable IDs/backlinks.
4. MongoDB and Qdrant adapter boundaries can write/read test entities without relying on later ingestion work.
5. Secrets, prompt inputs, logs, and rerun/idempotency behavior are designed before handling external content.

**Implementation Notes:**

- Keep provider integrations behind adapters from the start.
- Treat Markdown as canonical human-readable knowledge, with MongoDB as the structured metadata/relationship store and Qdrant as the vector query layer.
- Include a minimal UI shell because the selected v1 interface is website plus Markdown browser.

### Phase 2: TikTok Ingestion and Claim Extraction

**Status:** Complete (verified 2026-04-18)

**Goal:** Let a user submit a public TikTok URL or upload a user-owned video and turn the content into timestamped AI research claims with transcript and visual context.

**Requirements:** ING-01, ING-02, ING-03, ING-04, ING-05, CLM-01, CLM-02, CLM-03, UI-01

**UI hint:** yes

**Success Criteria:**

1. User can submit a public TikTok URL or upload a video file and receive a job ID with visible status.
2. The ingestion adapter records public metadata and media/transcript retrieval results without leaking platform-specific behavior outside the adapter.
3. The transcript pipeline uses available captions or a transcription fallback and stores provenance.
4. Claim extraction creates atomic claims with timestamps, transcript snippets, and screenshot references.
5. Failed ingestion and unsupported URLs produce clear, recoverable error states.

**Implementation Notes:**

- Complete a compliance review before implementing video download behavior.
- Keep pasted transcript or fixture-based ingestion available for tests and development.
- Do not couple TikTok behavior to claim extraction logic.

### Phase 3: Ground-Truth Discovery and Paper Processing

**Status:** Complete (verified 2026-04-18)

**Goal:** Find the right papers/preprints, process them into reusable evidence, and store paper knowledge as Markdown plus indexed chunks.

**Requirements:** SRC-01, SRC-02, SRC-03, SRC-04, SRC-05, PPR-01, PPR-02, PPR-03, PPR-04, PPR-05

**UI hint:** no

**Success Criteria:**

1. For each claim, the system can query live web search and paper indexes for candidate papers/preprints.
2. Candidate sources are merged and deduplicated using DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, title, and authors.
3. The system records why sources were selected, rejected, or marked supplemental.
4. Publicly accessible papers are linked or downloaded, parsed into chunks, summarized as Markdown, and indexed.
5. Paper Markdown notes include methods, claims, limitations, authors, source links, and provenance.

**Implementation Notes:**

- Prefer source precision over broad recall in v1.
- Mark preprint status explicitly.
- Every chunk inserted into Qdrant must trace back to a paper/source ID and Markdown note.

### Phase 4: Evidence Evaluation and Fact-Check Reports

**Goal:** Compare each video claim against stored source evidence and produce cited, uncertainty-aware fact-check reports.

**Requirements:** EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, UI-02

**UI hint:** yes

**Success Criteria:**

1. Every extracted claim is evaluated against stored source evidence records.
2. Each claim receives exactly one label: supported, contradicted, mixed, or insufficient evidence.
3. Supported, contradicted, and mixed labels cite stored evidence records and source links.
4. Reports explain uncertainty, source limitations, preprint status, and unresolved ambiguity.
5. User can view the report page with claims, evidence, citations, screenshots, and a Markdown report link.

**Implementation Notes:**

- Reject uncited labels during report generation.
- Do not aggregate claim labels into a single truth score.
- Preserve all evaluation inputs so reports can be rerun as the knowledge base improves.

### Phase 5: Knowledge Browser, Search, Graph, and Ratings

**Goal:** Make the accumulated Markdown/vector/graph knowledge useful for future checks through browsing, search, graph inspection, consistency checks, and transparent ratings.

**Requirements:** KB-06, UI-03, UI-04, UI-05, RAT-01, RAT-02, RAT-03

**UI hint:** yes

**Success Criteria:**

1. User can browse Markdown notes for videos, creators, claims, papers, authors, sources, and reports in an Obsidian-like UI.
2. User can search stored notes, papers, claims, and reports through Qdrant-backed search with useful filters.
3. User can inspect graph relationships between creators, claims, papers, authors, sources, evidence, and topics.
4. System can run a consistency check across Markdown, MongoDB, and Qdrant and report drift.
5. Creator, paper, author, and source rating records show evidence count, label distribution, source basis, and confidence level.
6. Early ratings are marked experimental until enough evidence history exists.

**Implementation Notes:**

- Keep graph UI functional, not decorative: it should explain source trails and relationship context.
- Rating output must be auditable and conservative.
- Use Phase 5 to harden rerun/reindex workflows discovered in earlier phases.

## Requirement Coverage

| Requirement Group | Requirements | Phase |
|-------------------|--------------|-------|
| Foundation and stores | KB-01 to KB-05, OPS-01 to OPS-04 | Phase 1 |
| Ingestion and claims | ING-01 to ING-05, CLM-01 to CLM-03, UI-01 | Phase 2 |
| Source discovery and papers | SRC-01 to SRC-05, PPR-01 to PPR-05 | Phase 3 |
| Evaluation and reports | EVAL-01 to EVAL-05, UI-02 | Phase 4 |
| Knowledge UI and ratings | KB-06, UI-03 to UI-05, RAT-01 to RAT-03 | Phase 5 |

## Verification Strategy

- Each phase must verify user-facing behavior or stored artifacts, not just implementation tasks.
- Each phase must include tests for idempotency and traceability where it writes durable knowledge.
- Every generated report must be reproducible from stored claims, sources, and evidence records.
- The final milestone is complete only when a TikTok URL can flow through ingestion, claim extraction, source discovery, paper processing, evidence evaluation, Markdown storage, MongoDB relationship storage, vector indexing, and UI browsing.

---
*Roadmap created: 2026-04-18*
