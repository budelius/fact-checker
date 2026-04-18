# Phase 3 Ground Truth

## Scope

Phase 3 discovers candidate research sources for Phase 2 claims, keeps papers and preprints only as v1 ground truth, processes public papers into reusable owned knowledge, and stores traceable paper knowledge as Markdown plus MongoDB-compatible entities and Qdrant payloads.

Phase 3 does not decide whether a claim is supported, contradicted, mixed, or insufficient. Phase 4 owns evidence evaluation and fact-check labels.

## API Routes

- `POST /ground-truth/jobs/from-ingestion/{ingestion_job_uuid}` starts source discovery and paper processing from a completed ingestion job.
- `GET /ground-truth/jobs/{job_uuid}` returns the stored ground-truth job or `ground_truth_job_not_found`.

The start route returns `ingestion_job_not_found` when the Phase 2 job does not exist and `ingestion_job_has_no_claims` when the ingestion payload has no extracted claims.

## Provider Policy

Discovery combines Phase 2 source hints, extracted claims, transcript excerpts, and screenshot clue text. Provider adapters normalize results from:

- OpenAI web search with URL citations and `web_search_call.action.sources`.
- arXiv Atom API results.
- OpenAlex Works results.
- Semantic Scholar paper results.

Provider output is never trusted directly. Results become `PaperCandidate` records and are merged by DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, normalized URL, and title/authors fallback.

## Ground-Truth Policy

v1 ground truth is papers and preprints only. Non-paper sources such as articles, blogs, product pages, or explainers are retained as supplemental provenance and cannot become selected ground truth.

When no acceptable paper or preprint is selected, the system returns:

`No scientific evidence found for now.`

The machine-readable reason is:

`no_scientific_evidence_found_for_now`

This means the Phase 3 discovery pipeline did not find an acceptable paper/preprint in the current run. It does not prove that no paper exists anywhere.

## Paper Processing

Public paper PDFs are downloaded only when a URL appears lawfully public, PDF-like, and within size limits. The system does not bypass paywalls, authentication, signed URLs, local/private hosts, or publisher access controls. If the PDF cannot be downloaded or parsed, the paper remains linked or metadata-only.

Downloaded PDFs are stored under:

`vault/raw/papers/`

Parsed text becomes deterministic `PaperChunk` records with paper UUID, source UUID, vault path, source URL, page range, and chunk ID.

## Markdown Output

Paper notes are written under:

`vault/wiki/papers/`

Each note includes frontmatter for UUID, entity type, slug, title, aliases, external IDs, relationships, and timestamps. The body includes source links, abstract, methods, key claims, limitations, references, and provenance.

## Storage And Indexing

MongoDB-compatible persistence writes paper, author, and evidence entities plus `authored_by`, `derived_from`, and `cites` relationships. Qdrant payloads index both paper chunks and paper summaries with vault path, chunk ID, source, source UUID, and relationship UUID trace fields.

Tests use fake providers, fake repositories, fake Qdrant, and fake embedding vectors. They do not call live provider APIs.

## Traceability

Phase 3 logs source discovery stages for claim loading, query generation, OpenAI web search, paper-index search, candidate merging, and source selection. Provider citations, source URLs, selected/rejected/supplemental reasons, PDF acquisition results, parse status, chunk IDs, Markdown paths, and index payloads stay inspectable.

## Verification

```bash
cd backend && uv run pytest -q
```
