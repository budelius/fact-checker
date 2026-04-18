# Phase 3: Ground-Truth Discovery and Paper Processing - Research

**Researched:** 2026-04-18
**Domain:** Source discovery, scholarly API lookup, paper processing, Markdown vault persistence, vector indexing, provenance logging
**Confidence:** HIGH for planning, MEDIUM for exact provider response fields until implementation verifies live API responses.
**Network:** Used primary documentation sources for OpenAI, arXiv, OpenAlex, Semantic Scholar, and pypdf.

<user_constraints>
## User Constraints From CONTEXT.md

Phase 3 is locked to a full paper-processing workflow:

- Discovery should be creative and staged, combining Phase 2 hints, extracted identifiers, transcript phrasing, screenshot/source-clue text, title-like spans, author-like names, named studies, and query variants.
- Search must use both OpenAI live web search and paper indexes such as arXiv, OpenAlex, and Semantic Scholar.
- v1 ground truth must be a paper or preprint. Non-paper sources can be supplemental context only.
- If no relevant paper/preprint can be found, the system says there is no scientific evidence found for now, without implying no paper exists anywhere.
- The workflow should search, merge/dedupe, select/reject, link or lawfully download papers, parse text, chunk content, summarize Markdown, write structured records, and index chunks.
- Traceability is a first-class requirement: queries, provider results, ranks, merge decisions, selected/rejected reasons, download/link decisions, parse status, chunk IDs, summarization metadata, and index writes should be logged.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Planning Implication |
|----|-------------|----------------------|
| SRC-01 | Search for relevant papers and preprints using OpenAI live web search with citation capture. | Add an OpenAI web-search adapter that records citations and full source lists, not just model prose. |
| SRC-02 | Search paper indexes such as OpenAlex, Semantic Scholar, and arXiv. | Add explicit provider clients with deterministic tests and no network calls in CI. |
| SRC-03 | Merge candidates by DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, title, and authors. | Add canonical candidate schema, normalization, and dedupe scoring before selection. |
| SRC-04 | Record why a candidate paper was selected or rejected. | Store source decisions and rejection reasons as durable records and Markdown-visible provenance. |
| SRC-05 | Reject or mark non-paper sources as supplemental rather than v1 ground truth. | Candidate status enum must distinguish selected paper, rejected paper, supplemental non-paper, no paper found, and needs manual review. |
| PPR-01 | Store paper metadata including title, authors, source, status, date, DOI/arXiv URL, and source links. | Paper metadata schema must preserve publication/preprint status plus provider identifiers. |
| PPR-02 | Download or link paper PDFs when available through lawful public access. | Add acquisition policy, size limits, access checks, and processing statuses; no paywall bypass. |
| PPR-03 | Parse paper text into reusable chunks with source metadata. | Add pypdf parsing and chunk model with page/section/source trace fields. |
| PPR-04 | Summarize each paper as Markdown with claims, methods, limitations, links, references, and provenance. | Add Markdown builder and structured summarization output, with deterministic fallback for tests. |
| PPR-05 | Index paper chunks and summaries for retrieval. | Add embedding service and Qdrant upsert path using existing payload trace fields. |

</phase_requirements>

## Primary Recommendation

Plan Phase 3 as a backend-only pipeline with six slices:

1. Contracts and dependencies.
2. Provider clients for OpenAI web search and scholarly indexes.
3. Discovery orchestration, dedupe, selection, and no-evidence policy.
4. Lawful paper acquisition, PDF parsing, and chunking.
5. Markdown, MongoDB, embedding, and Qdrant persistence.
6. API integration, E2E fixture verification, docs, and requirement handoff.

Do not make Phase 3 evaluate claims as supported or contradicted. It should produce reusable evidence records and paper knowledge that Phase 4 can evaluate.

## External Source Findings

### OpenAI Web Search And Structured Outputs

OpenAI web search is available as a Responses API tool and can include URL citations in message annotations. The docs also expose a `sources` include path that returns the complete set of URLs consulted, which is important for transparent trace logs. Domain filtering is available with the `web_search` tool in the Responses API and can allow up to 100 allowed domains. Source: https://developers.openai.com/api/docs/guides/tools-web-search

Planning implications:

- The adapter should request web search through Responses API and store both inline citations and `web_search_call.action.sources`.
- For paper discovery, useful allow-list domains include `arxiv.org`, `openreview.net`, `aclanthology.org`, `proceedings.neurips.cc`, `proceedings.mlr.press`, `jmlr.org`, `semanticscholar.org`, `openalex.org`, and publisher domains only as supplemental hints.
- The adapter should never accept a web result as ground truth until it is normalized into a paper/preprint candidate.

OpenAI structured outputs support JSON schema with strict mode. Source: https://developers.openai.com/api/docs/guides/structured-outputs

Planning implications:

- Use structured outputs for query generation, paper summaries, and extraction of methods/limitations from parsed paper text.
- Treat model output as generated data that must be schema-validated before persistence.
- Keep raw paper/web content wrapped by `backend/app/safety/input_boundaries.py` before LLM use.

OpenAI embeddings accept string or array input, have per-input token limits, and support `text-embedding-3-small` and `text-embedding-3-large`; `dimensions` is supported for `text-embedding-3` and later. Source: https://developers.openai.com/api/reference/resources/embeddings/methods/create

Planning implications:

- Use `text-embedding-3-small` as the first default for cost-sensitive chunk indexing unless the user later opts into higher recall/cost.
- Do not hard-code a vector dimension from memory. Either read configured dimensions or infer from the first returned embedding before `QdrantRepository.ensure_collection`.
- Batch embeddings, but tests should use deterministic fake vectors.

### arXiv API

The arXiv API query endpoint uses `export.arxiv.org/api/query` and returns Atom XML. Its query parameters include `search_query`, `id_list`, `start`, `max_results`, `sortBy`, and `sortOrder`; `id_list` can directly retrieve known arXiv IDs. The manual asks clients to play nicely with delays in repeated calls and recommends smaller result slices/refined queries for large result sets. Source: https://info.arxiv.org/help/api/user-manual.html

Planning implications:

- arXiv exact ID lookup should be the first path for `arxiv` Phase 2 candidates.
- Query variants can use field prefixes such as title and author through `search_query`.
- Parse Atom entries for title, abstract summary, authors, categories, published/updated dates, DOI/journal refs when present, abstract URL, and PDF link.
- Implement a provider delay/cache boundary so repeated searches do not hammer arXiv.

### OpenAlex Works API

OpenAlex Works are scholarly documents and support filtering, sorting, grouping, and search across works. Fields include DOI, OpenAlex ID, publication date/year, authorship fields, open-access fields, PDF URL indicators, references, citation fields, retraction flags, and publication type. Source: https://developers.openalex.org/api-reference/works

Planning implications:

- OpenAlex should be used for DOI lookup, title/abstract search, open-access status, publication type, retraction flags, reference metadata, and OA PDF/link discovery.
- Use `select` to keep responses small and store the raw provider result in trace metadata.
- Treat `is_retracted` as a major rejection or warning reason.
- Use OpenAlex IDs as external IDs, never canonical UUIDs.

### Semantic Scholar API

Semantic Scholar provides Academic Graph, Recommendations, and Datasets APIs. Academic Graph returns paper, author, citation, reference, venue, embedding, and page-link metadata. API keys are optional for some endpoints but recommended; the public page notes shared unauthenticated limits and an introductory authenticated rate of 1 request per second. Source: https://www.semanticscholar.org/product/api

The tutorial recommends paper bulk search for most keyword-search cases and shows fields such as `title`, `url`, `publicationTypes`, `publicationDate`, and `openAccessPdf`; paper details can return fields such as title, year, abstract, and citation count. Source: https://www.semanticscholar.org/product/api/tutorial

Planning implications:

- Use Semantic Scholar for paper search, paper detail lookup, openAccessPdf links, references/citations, author metadata, and publication type.
- Store API key in environment/config only; never write it into Markdown or trace logs.
- Respect rate limits and add provider result caching where practical.

### PDF Parsing

pypdf is a pure-Python PDF library that can retrieve text and metadata from PDFs. Its docs show `PdfReader(...).pages[0].extract_text()` and document caveats: large content streams can be memory-heavy, and scanned/image-only PDFs may produce little or no text and may need OCR. Source: https://pypdf.readthedocs.io/

Planning implications:

- Add `pypdf` for Phase 3 parsing because it is simpler than native dependencies and good enough for MVP text extraction.
- Enforce PDF size and page/content-stream safeguards.
- Store `parse_status=metadata_only` or `parse_status=text_unavailable` for scanned/image-only PDFs rather than pretending chunks exist.

## Architecture Responsibility Map

| Capability | Primary Module | Persistence | Notes |
|------------|----------------|-------------|-------|
| Source hint loading | `ground_truth/discovery.py` | Ingestion job payload | Reads Phase 2 claims and `research_basis` candidates. |
| Query generation | `ground_truth/queries.py` | Trace events | Uses identifiers, claim text, transcript excerpts, screenshot clue text, and title-like spans. |
| Provider calls | `ground_truth/clients/*` | Trace events | All network behavior is isolated and mockable. |
| Candidate normalization | `schemas/ground_truth.py`, `ground_truth/dedupe.py` | MongoDB/source notes | DOI/arXiv/OpenAlex/S2 IDs are aliases/external IDs. |
| Selection policy | `ground_truth/selection.py` | Decision records | Only papers/preprints become selected ground truth. |
| Paper acquisition | `ground_truth/acquisition.py` | `vault/raw/papers/` | Download only public lawful PDFs, otherwise link/metadata-only. |
| Paper parsing/chunking | `ground_truth/parsing.py`, `ground_truth/chunking.py` | Evidence chunk records | Chunks trace to paper UUID, source URL, page/section, and raw/vault path. |
| Summarization | `ground_truth/summarization.py` | Paper Markdown note | Use structured output and deterministic fallback for tests. |
| Indexing | `ground_truth/indexing.py` | Qdrant | Existing payload contract must preserve UUID, chunk ID, source UUID, relationship UUIDs. |
| API orchestration | `api/ground_truth.py` | Job store and events | Trigger Phase 3 from an ingestion job UUID; no UI required in this phase. |

## Data Model Recommendations

Add `backend/app/schemas/ground_truth.py` with:

- `GroundTruthJob`, `GroundTruthStage`, `GroundTruthArtifact`
- `SourceProvider`: `phase2_hint`, `openai_web`, `arxiv`, `openalex`, `semantic_scholar`
- `CandidateKind`: `paper`, `preprint`, `non_paper`, `unknown`
- `CandidateStatus`: `selected_ground_truth`, `rejected`, `supplemental`, `no_paper_found`, `needs_manual_review`
- `ExternalPaperId` for DOI, arXiv, OpenAlex, Semantic Scholar, URL
- `PaperCandidate`
- `SourceDecision`
- `PaperMetadata`
- `PaperAuthor`
- `PaperAcquisition`
- `PaperChunk`
- `PaperSummary`

Keep Phase 2 `ResearchBasisCandidate` as input; do not mutate it into evidence. Phase 3 can map it into `PaperCandidate.discovery_paths`.

## Storage Recommendations

- Extend `VAULT_RAW_ARTIFACT_FOLDERS` with `papers`.
- Use `vault/raw/papers/{slug}.pdf` for downloaded public PDFs.
- Use `vault/wiki/papers/{slug}.md` for paper notes.
- Use `vault/wiki/sources/{slug}.md` for source/provider notes when useful.
- Use `vault/wiki/evidence/{slug}.md` for chunk/evidence notes only if the chunk deserves human-readable standalone context; Qdrant payloads must always trace to a vault path.
- Store MongoDB canonical entities for paper/source/author/evidence plus relationships:
  - claim `cites` paper/source candidate
  - paper `authored_by` author
  - evidence `derived_from` paper
  - paper/source `related_to` claim/video when selected
- Store rejected/supplemental decisions either as source records or ground-truth job decision records. Do not discard them.

## Verification Strategy

The implementation should use deterministic provider fixtures:

- arXiv Atom XML fixture with `1706.03762`
- OpenAlex JSON fixture with DOI/open_access fields
- Semantic Scholar JSON fixture with `paperId`, `openAccessPdf`, `publicationTypes`, `publicationDate`
- OpenAI web-search fixture with citation annotations and `sources`
- tiny generated PDF fixture for pypdf parsing
- fake embedding provider returning stable vectors
- fake Qdrant repository collecting payloads

Coverage must prove:

- All ten Phase 3 requirement IDs appear in plan frontmatter and tests.
- No non-paper source can become selected ground truth.
- No-paper cases produce `no_scientific_evidence_found_for_now`.
- Duplicate candidates merge by DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, then normalized title/authors.
- Download attempts obey lawful public-access policy and metadata-only fallback.
- Every indexed chunk has paper/source UUID and vault path trace fields.

## Risks And Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Provider APIs change fields or rate limits | medium | Keep clients isolated, typed, and covered by fixture tests; document primary docs in code comments sparingly. |
| OpenAI web search finds articles/blogs and model prose overclaims them | high | Normalize every result into candidate records and enforce papers/preprints-only selection. |
| PDF parsing fails or returns noisy text | medium | Store parse status and metadata-only fallback; chunk only non-empty extracted text. |
| Paywalled or non-public PDFs are downloaded accidentally | high | Add acquisition policy with explicit allowed URL sources, content type checks, size limits, and no authentication/cookie use. |
| Reruns duplicate papers/authors/chunks | high | Upsert/dedupe by external IDs and deterministic chunk IDs. |
| Markdown and Qdrant drift | medium | Store trace keys and add E2E verification that vault path and Qdrant payload match. |

## Sources

- OpenAI web search docs: https://developers.openai.com/api/docs/guides/tools-web-search
- OpenAI structured outputs docs: https://developers.openai.com/api/docs/guides/structured-outputs
- OpenAI embeddings API reference: https://developers.openai.com/api/reference/resources/embeddings/methods/create
- arXiv API user manual: https://info.arxiv.org/help/api/user-manual.html
- OpenAlex Works API reference: https://developers.openalex.org/api-reference/works
- Semantic Scholar API overview: https://www.semanticscholar.org/product/api
- Semantic Scholar API tutorial: https://www.semanticscholar.org/product/api/tutorial
- pypdf documentation: https://pypdf.readthedocs.io/

---

## RESEARCH COMPLETE
