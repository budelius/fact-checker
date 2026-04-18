# Phase 3: Ground-Truth Discovery and Paper Processing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 03-ground-truth-discovery-and-paper-processing
**Areas discussed:** Source Discovery Strategy, Ground-Truth Acceptance Policy, Paper Processing Depth, Provenance And Selection Records

---

## Source Discovery Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Staged hybrid discovery | Combine Phase 2 hints, live web search, paper indexes, identifiers, transcript text, screenshot clues, and query expansion. | yes |
| Exact hint lookup only | Only resolve explicit DOI, arXiv ID, title, or URL candidates from Phase 2. | |
| Broad web-first discovery | Use broad web search first, then try to identify papers after the fact. | |

**User's choice:** "be creative"

**Notes:** Interpreted as permission to use a creative staged search strategy, including multiple clue sources and query variants. Acceptance remains strict: only papers/preprints become v1 ground truth.

---

## Ground-Truth Acceptance Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Papers/preprints only | Accept only research papers or preprints as ground truth; if none found, say no scientific evidence found for now. | yes |
| Papers plus reputable news | Accept papers and selected news/articles as ground truth. | |
| Any credible source | Accept papers, news, blogs, vendor docs, and commentary with source-tier weighting. | |

**User's choice:** "gt must be a paper if not just tell that there is not scientific evidence for now"

**Notes:** Non-paper sources may be logged as supplemental discovery context but must not be used as v1 ground truth.

---

## Paper Processing Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Full workflow | Search, merge/dedupe, select/reject, link/download lawful papers, parse, chunk, summarize Markdown, write records, and index chunks. | yes |
| Metadata first | Store identifiers, links, abstracts, and candidate decisions; defer parsing/chunking/summaries. | |
| Links only | Save source links and selected/rejected status without local paper knowledge processing. | |

**User's choice:** "the full workflow"

**Notes:** Phase 3 should implement the complete paper-processing loop needed by Phase 4, while still avoiding claim truth evaluation.

---

## Provenance And Selection Records

| Option | Description | Selected |
|--------|-------------|----------|
| Full trace logging | Store queries, providers, results, merge keys, selected/rejected reasons, processing statuses, chunks, and index writes. | yes |
| Selected-only provenance | Store selected sources and basic processing status, but discard most rejected-candidate details. | |
| Minimal audit trail | Store final paper links and summaries only. | |

**User's choice:** "log as much as possible to be fully traceable and transparent"

**Notes:** Rejected candidates, supplemental non-paper sources, and all discovery/processing decisions should remain inspectable.

---

## the agent's Discretion

- Exact provider clients, query generation mechanics, parser/chunker selection, and scoring formulas are left to downstream research and planning.

## Deferred Ideas

- Truth labels and fact-check reports remain Phase 4.
- Ratings and graph browsing remain Phase 5.
- Non-paper source tiers as ground truth remain future policy work.
