# Requirements: Fact Checker

**Defined:** 2026-04-18
**Core Value:** Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## v1 Requirements

Requirements for the first release. Each maps to roadmap phases.

### Ingestion

- [ ] **ING-01**: User can submit a public TikTok video URL from a website.
- [ ] **ING-02**: User can see whether a submitted fact-checking job is pending, running, failed, or complete.
- [ ] **ING-03**: System can retrieve public TikTok video metadata and media through a compliance-gated ingestion adapter.
- [ ] **ING-04**: System can retrieve source captions or generate a transcript when captions are unavailable.
- [ ] **ING-05**: System can capture representative screenshots or keyframes for visual context.

### Claims

- [ ] **CLM-01**: System can extract atomic AI research claims from the video transcript.
- [ ] **CLM-02**: Each extracted claim stores the source video, timestamp, transcript excerpt, and any relevant screenshot reference.
- [ ] **CLM-03**: System can preserve claim context separately from evidence so later evaluations can be rerun.

### Ground Truth

- [ ] **SRC-01**: System can search for relevant papers and preprints using OpenAI live web search with citation capture.
- [ ] **SRC-02**: System can search paper indexes such as OpenAlex, Semantic Scholar, and arXiv for candidate ground-truth sources.
- [ ] **SRC-03**: System can merge candidate sources by stable identifiers such as DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, title, and authors.
- [ ] **SRC-04**: System can record why a candidate paper was selected or rejected for a claim.
- [ ] **SRC-05**: System can reject or mark non-paper sources as supplemental rather than v1 ground truth.

### Papers

- [ ] **PPR-01**: System can store paper metadata including title, authors, source, publication/preprint status, date, DOI/arXiv URL when available, and source links.
- [ ] **PPR-02**: System can download or link paper PDFs when available through lawful public access.
- [ ] **PPR-03**: System can parse paper text into reusable chunks with source metadata.
- [ ] **PPR-04**: System can summarize each paper as Markdown with claims, methods, limitations, links, references, and provenance.
- [ ] **PPR-05**: System can index paper chunks and summaries for retrieval.

### Evaluation

- [ ] **EVAL-01**: System can compare each extracted video claim against selected source evidence.
- [ ] **EVAL-02**: System can label each claim as supported, contradicted, mixed, or insufficient evidence.
- [ ] **EVAL-03**: Every non-insufficient label cites stored evidence records and source links.
- [ ] **EVAL-04**: System can explain uncertainty, source limits, and preprint status in the report.
- [ ] **EVAL-05**: System can produce a complete Markdown fact-check report for each submitted video.

### Knowledge Base

- [ ] **KB-01**: System can create Obsidian-compatible Markdown notes for videos, creators, claims, papers, authors, sources, and reports.
- [ ] **KB-02**: Markdown notes use stable IDs and backlinks between related entities.
- [ ] **KB-03**: System can keep Markdown files as the canonical human-readable knowledge store.
- [ ] **KB-04**: System can index Markdown notes and source chunks in Qdrant with filters for entity type, source, date, and relationships.
- [ ] **KB-05**: System can write graph entities and relationships to Neo4j for creators, claims, papers, authors, sources, evidence, and topics.
- [ ] **KB-06**: System can run a consistency check between Markdown, Postgres metadata, Qdrant, and Neo4j.

### User Interface

- [ ] **UI-01**: User can paste a TikTok URL into a web form and start a fact-checking job.
- [ ] **UI-02**: User can view a report page with extracted claims, labels, evidence, citations, screenshots, and uncertainty notes.
- [ ] **UI-03**: User can browse the Markdown knowledge base through an Obsidian-like web UI.
- [ ] **UI-04**: User can search stored notes, papers, claims, and reports through a vector-backed search UI.
- [ ] **UI-05**: User can inspect graph relationships between creators, claims, papers, authors, sources, and evidence.

### Ratings

- [ ] **RAT-01**: System can create transparent rating records for creators, papers, authors, and sources based on accumulated evidence history.
- [ ] **RAT-02**: Each rating record shows the evidence count, label distribution, source basis, and confidence level.
- [ ] **RAT-03**: Early ratings are marked experimental until enough evidence history exists.

### Operations and Safety

- [ ] **OPS-01**: System stores API keys and provider credentials outside Markdown, logs, and committed files.
- [ ] **OPS-02**: System treats transcripts, paper text, and web content as untrusted input during LLM prompting.
- [ ] **OPS-03**: System logs enough pipeline detail to debug failed ingestion, search, parsing, evaluation, indexing, and graph writes.
- [ ] **OPS-04**: System can rerun a fact-check job without duplicating canonical entities or corrupting indexes.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Additional Inputs

- **INP-01**: User can submit public Instagram/Reels links.
- **INP-02**: User can submit links through a chat client.
- **INP-03**: User can submit links through OpenClaw.
- **INP-04**: User can upload video files directly.

### Real-Time Use Cases

- **REAL-01**: System can use smart glasses or streaming SDK input to fact-check videos in real time.
- **REAL-02**: System can act as a meeting assistant using the accumulated knowledge graph.

### Source Policy

- **POL-01**: User can configure source tiers that include reputable news, blogs, corporate pages, and expert commentary.
- **POL-02**: User can set organization-specific ground-truth policies.

### Provider Independence

- **PROV-01**: System can run with alternative LLM providers.
- **PROV-02**: System can run with local transcription and embedding models.
- **PROV-03**: System can support EU-only deployment constraints.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Instagram ingestion in v1 | TikTok public links are the first narrow target. |
| Chat client and OpenClaw submission in v1 | Website submission validates the core workflow first. |
| Smart glasses and real-time checking in v1 | Requires a reliable knowledge base and streaming-specific design. |
| News as normal v1 ground truth | Papers and preprints are the selected v1 source standard. |
| Binary true/false primary verdict | Evidence labels better represent uncertainty in research claims. |
| Opaque reputation scoring | Ratings must be traceable to evidence history. |
| Private or paywalled video ingestion | Adds privacy, legal, and access risks outside v1. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ING-01 | Phase 2 | Pending |
| ING-02 | Phase 2 | Pending |
| ING-03 | Phase 2 | Pending |
| ING-04 | Phase 2 | Pending |
| ING-05 | Phase 2 | Pending |
| CLM-01 | Phase 2 | Pending |
| CLM-02 | Phase 2 | Pending |
| CLM-03 | Phase 2 | Pending |
| SRC-01 | Phase 3 | Pending |
| SRC-02 | Phase 3 | Pending |
| SRC-03 | Phase 3 | Pending |
| SRC-04 | Phase 3 | Pending |
| SRC-05 | Phase 3 | Pending |
| PPR-01 | Phase 3 | Pending |
| PPR-02 | Phase 3 | Pending |
| PPR-03 | Phase 3 | Pending |
| PPR-04 | Phase 3 | Pending |
| PPR-05 | Phase 3 | Pending |
| EVAL-01 | Phase 4 | Pending |
| EVAL-02 | Phase 4 | Pending |
| EVAL-03 | Phase 4 | Pending |
| EVAL-04 | Phase 4 | Pending |
| EVAL-05 | Phase 4 | Pending |
| KB-01 | Phase 1 | Pending |
| KB-02 | Phase 1 | Pending |
| KB-03 | Phase 1 | Pending |
| KB-04 | Phase 1 | Pending |
| KB-05 | Phase 1 | Pending |
| KB-06 | Phase 5 | Pending |
| UI-01 | Phase 2 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 5 | Pending |
| UI-04 | Phase 5 | Pending |
| UI-05 | Phase 5 | Pending |
| RAT-01 | Phase 5 | Pending |
| RAT-02 | Phase 5 | Pending |
| RAT-03 | Phase 5 | Pending |
| OPS-01 | Phase 1 | Pending |
| OPS-02 | Phase 1 | Pending |
| OPS-03 | Phase 1 | Pending |
| OPS-04 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 41 total
- Mapped to phases: 41
- Unmapped: 0

---
*Requirements defined: 2026-04-18*
*Last updated: 2026-04-18 after roadmap creation*
