# Fact Checker

## What This Is

Fact Checker is a user-owned fact-checking system for AI research claims in public TikTok videos. A user pastes a video link into a website, the backend extracts the transcript and video context, finds relevant papers or preprints, and produces an evidence-backed report plus a growing Markdown knowledge base.

The product is not just a one-off checker. It builds an owned research memory over time: Markdown notes, vector search, and MongoDB-backed graph relationships connect videos, creators, claims, papers, authors, sources, and evidence so future checks become faster and more accurate.

## Core Value

Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## Requirements

### Validated

- [x] Phase 1 foundation contracts: monorepo structure, MongoDB/Qdrant local datastore contracts, UUID schemas, Markdown vault schema/templates, static knowledge-browser shell, and safety boundaries.

### Active

- [ ] User can paste a public TikTok video URL into a website and start a fact-checking job.
- [ ] System can retrieve or generate a transcript and capture video context for the submitted TikTok video.
- [ ] System can extract concrete AI research claims from the transcript and video context.
- [ ] System can search for relevant ground-truth sources, limited in v1 to research papers and preprints.
- [ ] System can download or link source papers when available and summarize them as Markdown with citations, authors, and references.
- [ ] System can compare extracted claims against evidence and label each claim as supported, contradicted, mixed, or insufficient evidence.
- [ ] System can create a Markdown knowledge base with notes for videos, creators, claims, papers, authors, sources, and fact-check reports.
- [ ] System can index the knowledge base and source chunks in Qdrant for vector search.
- [ ] System can store entities and relationships in MongoDB for source, author, paper, creator, claim, and evidence relationships.
- [ ] System can expose an Obsidian-like web UI for browsing Markdown notes, search results, graph relationships, and fact-check reports.
- [ ] System can generate transparent initial ratings for creators, papers, authors, and sources based on accumulated evidence history.

### Out of Scope

- Instagram ingestion in v1 - TikTok public links are the first narrow ingestion target.
- Chat client and OpenClaw submission flows in v1 - website submission proves the core loop first.
- Smart glasses, live meetings, and real-time video fact checking in v1 - these depend on a reliable knowledge base and evidence pipeline.
- Binary true/false verdicts as the primary output - v1 uses evidence labels and uncertainty because research claims are often contextual.
- News articles as normal ground truth in v1 - papers and preprints are the default; news can be added later as a lower-trust supplemental tier.
- Fully automated punitive creator scoring - ratings must remain transparent, explainable, and derived from evidence history.

## Context

The narrow first use case is AI research fact checking for public TikTok videos. The target workflow is:

1. User pastes a public TikTok link into a website.
2. Backend retrieves the public video and metadata through a compliant ingestion adapter.
3. Backend retrieves captions or transcribes the audio.
4. Backend extracts factual AI research claims from the transcript and selected video frames.
5. Backend searches the live web and paper indexes for relevant papers or preprints.
6. Backend downloads or links papers, indexes them, and summarizes them as Markdown.
7. Backend compares claims against evidence and produces claim-level labels.
8. Backend writes Markdown notes, MongoDB structured records/relationships, and vector index records.
9. User browses the report, Markdown knowledge base, search, and graph relationships in the web UI.

Why this needs to exist:

- Existing chat systems can answer fact-checking questions, but the user wants evidence memory that is owned by the user or company.
- The project should reduce vendor lock-in by keeping the durable knowledge in open Markdown plus independently controlled stores.
- The project should create awareness of hallucinations by making sources, uncertainty, and citation trails visible.
- The hybrid approach matters: LLMs are useful for extraction, search planning, summarization, and comparison, but the owned knowledge graph and source corpus provide the long-term accuracy layer.

Known terms:

- "Ground truth" means links to research papers or preprints in v1.
- "Truthness" should be represented as claim-level evidence labels, not as a single absolute truth score.
- "Knowledge graph" means explicit relationships across creators, papers, authors, claims, sources, entities, topics, evidence, and reports.

## Constraints

- **Ground truth**: v1 uses research papers and preprints only - this keeps evaluation anchored to research evidence before adding lower-trust source tiers.
- **Input source**: v1 supports public TikTok links only - one platform keeps ingestion risk contained.
- **Interface**: v1 uses a website with URL submission and an Obsidian-like Markdown browser - this validates the user workflow before chat clients or glasses.
- **Judgment model**: v1 labels claims as supported, contradicted, mixed, or insufficient evidence - binary truth is too brittle for research claims.
- **Storage ownership**: Markdown files are the canonical human-readable knowledge store - users and companies must be able to keep, inspect, and move their knowledge.
- **Structured storage**: MongoDB is the structured metadata and graph relationship store - it replaces separate Postgres and Neo4j services for v1 operational records, entity documents, rating snapshots, and relationship edges.
- **Vector storage**: Qdrant is the first vector store target - it supports dense, sparse, filtered, and hybrid retrieval patterns suitable for paper and note search.
- **LLM dependency**: OpenAI APIs are allowed for v1 search, extraction, transcription, and reasoning, but durable data must remain outside OpenAI-hosted memory.
- **Compliance**: TikTok ingestion must be isolated behind an adapter and checked against platform terms before implementation - video downloading can be brittle and policy-sensitive.
- **Transparency**: Every report and rating must cite the underlying claims and evidence - hidden scores undermine trust.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| v1 is an end-to-end thin slice | The project needs to prove the full loop from video link to evidence-backed knowledge base, even if each part starts basic. | - Pending |
| v1 ground truth is papers and preprints | AI research claims are best checked against papers and arXiv-style preprints before adding news or commentary. | - Pending |
| v1 uses evidence labels | Supported, contradicted, mixed, and insufficient evidence expose uncertainty better than a binary true/false verdict. | - Pending |
| v1 UI is website plus Markdown browser | URL submission plus knowledge browsing validates the main workflow and the owned-memory value proposition. | - Pending |
| v1 input is public TikTok links | TikTok is the narrow creator-platform target; Instagram is deferred. | - Pending |
| Markdown is the canonical knowledge surface | Markdown keeps the corpus portable, inspectable, and compatible with Obsidian-like workflows. | Validated in Phase 1 |
| MongoDB replaces Postgres and Neo4j | One document database keeps operational records, entity metadata, rating snapshots, and graph relationships together for the MVP, reducing local infrastructure and schema coordination. | Validated in Phase 1 |
| Qdrant is the vector database target | Qdrant fits filtered and hybrid retrieval for source chunks, claims, and notes. | Validated in Phase 1 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? Move to Out of Scope with reason
2. Requirements validated? Move to Validated with phase reference
3. New requirements emerged? Add to Active
4. Decisions to log? Add to Key Decisions
5. "What This Is" still accurate? Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-18 after Phase 1 verification*
