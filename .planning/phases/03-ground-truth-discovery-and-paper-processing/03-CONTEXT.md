# Phase 3: Ground-Truth Discovery and Paper Processing - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 takes Phase 2 ingestion outputs - extracted claims, transcript context, screenshots/keyframes, and research-basis candidates - and turns them into reusable paper knowledge. It searches for relevant papers and preprints, deduplicates candidates by stable identifiers, records selected/rejected/supplemental source decisions, downloads or links lawfully accessible papers, parses them into chunks, summarizes them as Markdown notes, writes source/paper/author/evidence records, and indexes paper chunks for retrieval.

This phase does not evaluate whether a video claim is supported, contradicted, mixed, or insufficient. Claim evaluation and fact-check reports belong to Phase 4. Creator, author, paper, and source ratings belong to Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Source Discovery Strategy

- **D-01:** Use a creative staged discovery strategy, not a single search call. The system should combine Phase 2 source hints, extracted identifiers, transcript phrasing, screenshot/source-clue text, title-like spans, author-like names, named studies, and generated query variants.
- **D-02:** Search should use both live web search and paper indexes. OpenAI live web search is allowed for broad discovery and citation capture, while paper indexes such as arXiv, OpenAlex, and Semantic Scholar should be used for paper-specific metadata, identifiers, and deduplication.
- **D-03:** Prefer source precision over broad recall, but allow exploratory expansion when the video contains weak or indirect clues. Creative expansion is allowed to find the likely referenced paper, but acceptance remains strict: only papers/preprints become v1 ground truth.
- **D-04:** Discovery should support multiple candidate paths: exact identifier lookup, exact title lookup, semantic/keyword query from claim text, visual clue query from screenshots/OCR, and backward/forward reference exploration where available.
- **D-05:** Discovery output should preserve the path by which each candidate was found so downstream users can understand whether the source came from an explicit DOI/arXiv ID, a title clue, a web result, a paper-index result, or an inferred query.

### Ground-Truth Acceptance Policy

- **D-06:** Ground truth for v1 must be a research paper or preprint. Papers include peer-reviewed publications and preprints such as arXiv-style records when clearly identifiable.
- **D-07:** Non-paper sources such as news articles, blog posts, social posts, creator captions, press releases, vendor pages, or commentary are not accepted as v1 ground truth. They may be recorded as supplemental source context only when useful for provenance or finding a paper.
- **D-08:** If no relevant paper or preprint can be found for a claim, the system should say there is no scientific evidence found for now. It must not manufacture a source or evaluate the claim against weaker source types as if they were ground truth.
- **D-09:** "No scientific evidence found for now" means the Phase 3 discovery pipeline did not find an acceptable paper/preprint. It is not a claim that no paper exists anywhere.
- **D-10:** Candidate status should distinguish selected ground-truth paper, rejected paper candidate, supplemental non-paper source, no paper found, and needs manual review.

### Paper Processing Depth

- **D-11:** Implement the full Phase 3 workflow, not a metadata-only placeholder. The workflow should search, merge/dedupe, select/reject, link or lawfully download papers, parse text, chunk paper content, summarize papers as Markdown, write structured records, and index chunks.
- **D-12:** Publicly accessible PDFs should be downloaded only through lawful public access. The system must not bypass paywalls, authentication, robots restrictions, or access controls.
- **D-13:** When a PDF cannot be lawfully downloaded, the system should still store paper metadata, stable links, abstracts when available through lawful APIs, and a clear processing status explaining why full-text parsing is unavailable.
- **D-14:** Paper Markdown notes should be useful to humans and future agents. At minimum they should capture title, authors, identifiers, source links, publication/preprint status, date, abstract/summary, methods, key claims, limitations, references where available, provenance, related video claims, and processing status.
- **D-15:** Paper chunks indexed in Qdrant must trace back to paper/source UUIDs, chunk IDs, source section/page when available, vault path, and relationship UUIDs. The indexed corpus must remain reproducible from stored Markdown/raw artifacts.

### Provenance And Traceability

- **D-16:** Log as much as practical to make the workflow fully traceable and transparent. The system should record search queries, providers, result URLs, result ranks where available, candidate merge decisions, dedupe keys, selected/rejected reasons, download/link decisions, parse status, chunk IDs, summarization inputs/outputs metadata, and index writes.
- **D-17:** Rejected candidates are important knowledge. Store why a candidate was rejected, such as wrong domain, wrong paper, weak title match, no relevance to claim, duplicate of another record, non-paper source, inaccessible full text, or needs manual review.
- **D-18:** Every selected paper/source/chunk must be traceable to the originating claim, video, transcript excerpt, source candidate, and discovery path when available.
- **D-19:** The system should prefer auditable, structured provenance over opaque agent reasoning. Human-readable Markdown should explain important choices, while MongoDB records should preserve normalized data for reruns and consistency checks.
- **D-20:** Pipeline reruns must avoid duplicating canonical paper/source/author entities. Existing records should be matched through stable identifiers first and title/author/date fallbacks second.

### the agent's Discretion

- Exact provider API client organization, module names, retry behavior, and query construction are left to research and planning.
- Exact paper parser and chunking library are left to research and planning, as long as lawful access, traceability, and reproducibility are preserved.
- Exact summary section headings may be adjusted during implementation if the Markdown remains readable and covers the required paper knowledge.
- Exact confidence scoring formula for candidate matches is left to the planner, but scores must be explainable and backed by stored evidence fields.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Phase Requirements

- `.planning/PROJECT.md` - Product vision, strict paper/preprint ground-truth constraint, owned Markdown brain, MongoDB/Qdrant storage split, and no hidden ratings/verdicts.
- `.planning/REQUIREMENTS.md` - Phase 3 requirements `SRC-01` to `SRC-05` and `PPR-01` to `PPR-05`.
- `.planning/ROADMAP.md` - Phase 3 goal, success criteria, and boundary against Phase 4 evaluation.
- `.planning/STATE.md` - Current phase status and handoff from Phase 2.

### Prior Phase Contracts

- `.planning/phases/01-foundation-and-knowledge-store-contracts/01-CONTEXT.md` - UUID identity, Markdown vault, MongoDB graph-like relationships, Qdrant payload traceability, and provider boundary decisions.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md` - Phase 2 handoff contract for extracted claims, transcript context, screenshots, and source-candidate triage.
- `docs/phase-1-contracts.md` - Store contracts, safety boundaries, and drift/idempotency expectations.
- `docs/phase-2-ingestion.md` - Ingestion routes, artifact types, research-basis triage, and explicit Phase 3 handoff.
- `vault/SCHEMA.md` - Canonical vault folders, frontmatter requirements, raw/wiki split, wiki-link conventions, and untrusted-source safety rule.

### Existing Code Contracts

- `backend/app/schemas/ingestion.py` - Research-basis candidate/status schema currently produced by Phase 2.
- `backend/app/schemas/claims.py` - Extracted claim schema with pending evidence status and source-candidate count.
- `backend/app/schemas/entities.py` - Canonical entity types and UUID identity model.
- `backend/app/schemas/relationships.py` - MongoDB relationship record shape and existing relationship types.
- `backend/app/schemas/vector_payloads.py` - Qdrant payload traceability fields.
- `backend/app/contracts/vault.py` - Vault path conventions for wiki notes and raw artifacts.
- `backend/app/repositories/mongo.py` - Existing MongoDB repository boundaries for entities, relationships, jobs, and pipeline events.
- `backend/app/repositories/qdrant.py` - Existing Qdrant upsert boundary and deterministic point ID behavior.
- `backend/app/safety/input_boundaries.py` - Required wrapping for untrusted paper, web, transcript, and screenshot text before LLM use.

### External APIs To Research During Planning

- OpenAI official API documentation - Current live web search, citations, structured outputs, embeddings, and file/text processing APIs must be checked during Phase 3 research.
- arXiv API documentation - Identifier lookup, search query syntax, and metadata fields.
- OpenAlex API documentation - DOI/title/author lookup, concept metadata, open-access location data, and dedupe identifiers.
- Semantic Scholar API documentation - Paper search, paper detail lookup, citation/reference metadata, and rate limits.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/ingestion/research_basis.py`: Already extracts DOI, arXiv, URL, and paper-like references from transcript and screenshot text. Phase 3 should consume these candidates rather than re-implementing Phase 2 triage.
- `backend/app/schemas/ingestion.py`: Provides `ResearchBasisCandidate`, `ResearchBasisTriage`, and `ResearchBasisStatus`; Phase 3 can extend or map these into source-discovery records.
- `backend/app/schemas/claims.py`: Extracted claims have UUIDs, transcript excerpts, timestamps, screenshot UUIDs, pending evidence status, and source-candidate counts.
- `backend/app/contracts/vault.py` and `vault/SCHEMA.md`: Provide path and frontmatter conventions for paper, source, author, evidence, and topic notes.
- `backend/app/repositories/mongo.py`: Existing `entities`, `relationships`, `ingestion_jobs`, and `pipeline_events` collections are the natural persistence boundary for Phase 3 records and trace logs.
- `backend/app/repositories/qdrant.py`: Existing Qdrant payload upsert can be reused for paper chunks once embeddings are generated.
- `backend/app/safety/input_boundaries.py`: Paper text, web snippets, abstracts, and search results must be treated as untrusted external content before LLM summarization.

### Established Patterns

- Backend code is Python/FastAPI with Pydantic schemas and direct repository/service modules.
- UUIDs are canonical. DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, URLs, and provider result IDs are external IDs or aliases.
- Markdown is the owned, human-readable layer; MongoDB and Qdrant are derived from or traceable to it.
- Phase 2 routes currently serialize complete job payloads with artifacts, stages, claims, and research-basis payloads.
- Tests use deterministic fixture paths and temporary vault roots to avoid external API calls and raw artifact churn.

### Integration Points

- Phase 3 should attach to completed ingestion jobs and their extracted claims/research-basis candidates.
- New backend modules should likely live under a source-discovery or papers domain, separate from TikTok-specific ingestion.
- Paper/source/author/evidence entities should be written to the vault and MongoDB using shared UUID identity.
- Qdrant payloads for paper chunks should include source UUIDs, relationship UUIDs, chunk IDs, vault paths, and entity types.
- Pipeline events should record searchable trace entries for source discovery, candidate selection, paper processing, summarization, and indexing.

</code_context>

<specifics>
## Specific Ideas

- "Be creative" applies to discovery strategy: use multiple clues and search paths to find the likely referenced paper.
- Ground truth must be a paper/preprint. If no acceptable paper is found, tell the user there is no scientific evidence found for now.
- Build the full paper-processing workflow in Phase 3 rather than stopping at metadata.
- Log as much as possible so the process is fully traceable and transparent.

</specifics>

<deferred>
## Deferred Ideas

- Claim truth labels, cited fact-check reports, and user-facing report pages - Phase 4.
- Creator, paper, author, and source ratings - Phase 5.
- Treating news or other non-paper sources as ground truth - future source-policy work, not v1 Phase 3.
- Dedicated graph database beyond MongoDB - deferred from Phase 1 and still out of scope.

</deferred>

---

*Phase: 03-ground-truth-discovery-and-paper-processing*
*Context gathered: 2026-04-18*
