# Fact Checker

## Current State

**Shipped version:** v1.0 MVP on 2026-04-18
**Current milestone:** v1.1 Report Generation Responsiveness
**Status:** Planning v1.1 around async report generation and report UX.

Fact Checker v1.0 can take TikTok-oriented inputs, extract timestamped AI research claims, discover relevant papers or preprints, process source evidence, generate cited fact-check reports, and expose the resulting owned knowledge through a web vault browser with search, graph inspection, consistency checks, annotations, and evidence-state ratings.

## Current Milestone: v1.1 Report Generation Responsiveness

The next product fix is to make report generation feel trustworthy and usable. Today the frontend-triggered "Generate report" path can still spend a long time synchronously running Phase 3 live paper discovery and processing before Phase 4 evaluation. It no longer fails as a misleading fake CORS issue, but the user experience is still poor because the UI blocks behind a long request and does not make the work, limits, or recovery path clear.

v1.1 focuses on:

- Making ground-truth discovery and report generation truly async/pollable from the user's perspective.
- Returning a job identity immediately and preserving progress across refreshes.
- Limiting live paper discovery/processing for UI-triggered runs, with full refresh available when explicitly chosen.
- Reusing stored evidence where possible before launching expensive provider calls.
- Redesigning the report-generation UX so users can understand what is happening, why it is taking time, what limits apply, and what to do after errors.

## What This Is

Fact Checker is a user-owned fact-checking system for AI research claims in public TikTok videos. A user pastes a video link into a website, the backend extracts the transcript and video context, finds relevant papers or preprints, produces an evidence-backed report, and stores the result in a growing Markdown knowledge base with vector and graph indexes.

The product is not just a one-off checker. The durable output is a **personal research brain** — a human-readable knowledge graph the user owns. Every check writes into it: Markdown notes, vector search, and MongoDB-backed graph relationships connect videos, creators, claims, papers, authors, sources, and evidence, so future checks become faster and more accurate. Because the graph is human-readable it is inspectable, and because it is connected it becomes a second signal for fact-checking — contradictions that span the brain catch what a single paper cannot. Like Notion, but self-owned, extensible, and it fact-checks itself.

## Core Value

Own the knowledge, not just the verdict. Fact Checker saves time verifying AI research claims *and* accumulates the evidence and relationships into an owned, inspectable knowledge graph that the user or company keeps. Graph topology — not just claim-level labels — becomes a second measurement for truth as the brain grows.

## Requirements

### Validated

- [x] Phase 1 foundation contracts: monorepo structure, MongoDB/Qdrant local datastore contracts, UUID schemas, Markdown vault schema/templates, static knowledge-browser shell, and safety boundaries.
- ✓ Public TikTok URL and local upload submission workflow with visible job status — v1.0
- ✓ Transcript, screenshot/keyframe, and timestamped claim extraction artifacts — v1.0
- ✓ Paper/preprint discovery, dedupe, source selection/rejection, lawful PDF acquisition, parsing, summaries, and Qdrant indexing — v1.0
- ✓ Evidence evaluation with supported, contradicted, mixed, and insufficient labels plus cited Markdown fact-check reports — v1.0
- ✓ Markdown canonical knowledge store with MongoDB entities/relationships and Qdrant vector payloads — v1.0
- ✓ Page-first knowledge browser, command-palette search, graph inspection, consistency checks, annotations, and evidence-state ratings — v1.0

### Active

- [ ] v1.1 async report generation and responsive report UX requirements.

### Out of Scope

- Instagram ingestion in v1 - TikTok public links are the first narrow ingestion target.
- Chat client and OpenClaw submission flows in v1 - website submission proves the core loop first.
- Smart glasses, live meetings, and real-time video fact checking in v1 - these depend on a reliable knowledge base and evidence pipeline.
- Binary true/false verdicts as the primary output - v1 uses evidence labels and uncertainty because research claims are often contextual.
- News articles as normal ground truth in v1 - papers and preprints are the default; news can be added later as a lower-trust supplemental tier.
- Fully automated punitive creator scoring - ratings must remain transparent, explainable, and derived from evidence history.

## Context

The v1.0 MVP implements the narrow first use case: AI research fact checking for public TikTok videos and local/user-owned video fixtures. The target workflow is:

1. User pastes a public TikTok link into a website.
2. Backend retrieves the public video and metadata through a compliant ingestion adapter.
3. Backend retrieves captions or transcribes the audio.
4. Backend extracts factual AI research claims from the transcript and selected video frames.
5. Backend searches the live web and paper indexes for relevant papers or preprints.
6. Backend downloads or links papers, indexes them, and summarizes them as Markdown.
7. Backend compares claims against evidence and produces claim-level labels.
8. Backend writes Markdown notes, MongoDB structured records/relationships, and vector index records.
9. User browses the report, Markdown knowledge base, search, and graph relationships in the web UI.

Current codebase state after v1.0:

- Backend: FastAPI with Pydantic contracts, MongoDB repository boundary, Qdrant repository boundary, ingestion, ground-truth discovery, evaluation/reporting, and knowledge browser APIs.
- Frontend: React/Vite/Yarn workspace with ingestion workbench, report page, page-first knowledge browser, command palette, graph/consistency panels, annotations, and rating badges.
- Durable knowledge: Markdown under `vault/wiki/`, raw inputs under `vault/raw/`, MongoDB entities/relationships/annotations, and Qdrant payloads traceable to UUIDs and vault paths.
- Verification at close: 183 backend tests passed, frontend production build passed, and Phase 5 rating-copy safety grep passed.

Known v1.1 product issue:

- Report generation from the UI still couples long-running ground-truth discovery/paper processing with report creation. The current frontend waits on the full sequence, exposes limited progress, and makes slow or failed runs feel broken even when the backend is doing valid work.

Why this needs to exist:

- Existing chat systems can answer fact-checking questions, but the user wants evidence memory that is owned by the user or company.
- The project should reduce vendor lock-in by keeping the durable knowledge in open Markdown plus independently controlled stores.
- The project should create awareness of hallucinations by making sources, uncertainty, and citation trails visible.
- The hybrid approach matters: LLMs are useful for extraction, search planning, summarization, and comparison, but the owned knowledge graph and source corpus provide the long-term accuracy layer.
- The knowledge graph is itself an evidence mechanism. As the brain grows, cross-entity relationships (creator ↔ paper ↔ author ↔ claim) surface contradictions and corroborations that no single paper can reveal — this is the "second signal" that complements claim-level labels.
- The brain must be human-readable and portable. Markdown plus explicit IDs/backlinks means users can audit, extend, and migrate it — the antithesis of a closed chat-vendor memory.

Known terms:

- "Ground truth" means links to research papers or preprints in v1.
- "Truthness" should be represented as claim-level evidence labels, not as a single absolute truth score.
- "Knowledge graph" means explicit relationships across creators, papers, authors, claims, sources, entities, topics, evidence, and reports.
- "Personal brain" is the user's owned, Markdown-canonical knowledge graph that accumulates across checks. It is the primary durable artifact, not a side effect of reports.
- "Second signal" means evaluating a claim against graph topology (related claims, shared authors, cross-video contradictions) in addition to direct paper-level evidence.

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
| v1 is an end-to-end thin slice | The project needs to prove the full loop from video link to evidence-backed knowledge base, even if each part starts basic. | Validated in v1.0 |
| v1 ground truth is papers and preprints | AI research claims are best checked against papers and arXiv-style preprints before adding news or commentary. | Validated in v1.0 |
| v1 uses evidence labels | Supported, contradicted, mixed, and insufficient evidence expose uncertainty better than a binary true/false verdict. | Validated in v1.0 |
| v1 UI is website plus Markdown browser | URL submission plus knowledge browsing validates the main workflow and the owned-memory value proposition. | Validated in v1.0 |
| v1 input is public TikTok links | TikTok is the narrow creator-platform target; Instagram is deferred. | Validated in v1.0 |
| Markdown is the canonical knowledge surface | Markdown keeps the corpus portable, inspectable, and compatible with Obsidian-like workflows. | Validated in Phase 1 |
| MongoDB replaces Postgres and Neo4j | One document database keeps operational records, entity metadata, rating snapshots, and graph relationships together for the MVP, reducing local infrastructure and schema coordination. | Validated in Phase 1 |
| Qdrant is the vector database target | Qdrant fits filtered and hybrid retrieval for source chunks, claims, and notes. | Validated in Phase 1 |
| The personal brain is the primary artifact | Framing the knowledge graph as the product (not as a side effect of reports) shapes storage, UI, and evaluation priorities — reports are views into the brain, not the other way around. | Validated in v1.0 |
| Graph topology is a second signal for truth | Beyond paper-level citations, cross-entity graph relationships must be usable as evidence surface — contradictions and corroborations across the brain feed back into claim evaluation and rating confidence. | Initial browser/graph surface validated in v1.0 |
| Ratings use evidence-state badges | Badge language avoids hidden trust or reputation scoring while exposing evidence count, label distribution, source basis, and confidence. | Validated in v1.0 |
| Report generation must be job-oriented | Live discovery, paper processing, evaluation, Markdown writing, and indexing can exceed a normal request/attention window, so the product should expose durable progress and recovery instead of blocking behind one POST. | Active in v1.1 |

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
*Last updated: 2026-04-18 for v1.1 milestone initialization*
