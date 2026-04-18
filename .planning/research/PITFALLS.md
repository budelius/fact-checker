# Pitfalls Research

**Domain:** AI research fact checking for creator videos
**Researched:** 2026-04-18
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Hallucinated or Weak Citations

**What goes wrong:**
The report cites papers that do not support the claim, cites search snippets instead of source text, or invents confident conclusions from partial evidence.

**Why it happens:**
LLMs are good at plausible synthesis and bad at source discipline unless the workflow forces citation grounding.

**How to avoid:**
Require every claim label to point to stored source chunks, paper metadata, and links. Treat uncited labels as invalid.

**Warning signs:**
Reports contain vague citations, missing DOI/arXiv links, no page/chunk references, or confident labels with only one weak source.

**Phase to address:**
Phase 4: Evidence Evaluation and Report Generation.

---

### Pitfall 2: Matching the Wrong Paper

**What goes wrong:**
The creator references one paper, but the system evaluates against a related but different paper.

**Why it happens:**
Video creators often show screenshots, abbreviate titles, paraphrase claims, or refer to broad AI topics.

**How to avoid:**
Rank candidate sources using transcript text, screenshot OCR, visible titles/authors, dates, arXiv IDs, DOI strings, and citation context. Mark uncertain matches explicitly.

**Warning signs:**
Many candidate papers have similar titles; the selected paper lacks terms visible in the video; the report never explains why the source was selected.

**Phase to address:**
Phase 3: Ground-Truth Discovery and Paper Processing.

---

### Pitfall 3: Treating Preprints as Final Truth

**What goes wrong:**
The system treats arXiv/preprint claims as settled fact.

**Why it happens:**
AI research often circulates first as preprints, and creator content may discuss fresh results before peer review.

**How to avoid:**
Track source type, publication status, venue, date, citations, limitations, and paper confidence separately from claim labels.

**Warning signs:**
Reports do not distinguish peer-reviewed papers from preprints or ignore limitations sections.

**Phase to address:**
Phase 3 and Phase 4.

---

### Pitfall 4: Knowledge Store Drift

**What goes wrong:**
Markdown, Postgres, Qdrant, and Neo4j disagree about entities, source IDs, or latest labels.

**Why it happens:**
Multiple stores are necessary but can diverge without stable IDs and reindexing checks.

**How to avoid:**
Use stable IDs for every video, claim, paper, author, source, and report. Add idempotent writers and consistency checks.

**Warning signs:**
Search returns notes that no longer exist; graph links point to missing Markdown; report labels differ between UI and files.

**Phase to address:**
Phase 1 and Phase 5.

---

### Pitfall 5: Platform Ingestion Risk

**What goes wrong:**
TikTok ingestion breaks, violates terms, or depends on fragile page markup.

**Why it happens:**
Social platforms change APIs, markup, access controls, and terms.

**How to avoid:**
Make TikTok ingestion a replaceable adapter, document allowed behavior, and add fallback paths such as pasted transcript or uploaded test fixture for development.

**Warning signs:**
Downloader code is scattered through the app; tests require live TikTok; there is no compliance decision log.

**Phase to address:**
Phase 2: TikTok Ingestion and Claim Extraction.

---

### Pitfall 6: Opaque or Defamatory Ratings

**What goes wrong:**
The system assigns creator, author, paper, or source scores without clear evidence, creating trust and legal risk.

**Why it happens:**
Ratings are tempting as a final product metric, but reputation is contextual and sensitive.

**How to avoid:**
Use transparent rating records derived from evidence history, show inputs, and label early ratings as experimental.

**Warning signs:**
Single creator scores appear before enough claim history exists; users cannot trace rating inputs.

**Phase to address:**
Phase 5: Knowledge Browser, Search, Graph, and Ratings.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Store only generated summaries | Faster implementation | Cannot audit evidence or rebuild ratings | Never for claim labels |
| Skip stable entity IDs | Faster initial writes | Graph/vector/Markdown drift | Never |
| Hardcode OpenAI calls | Fast prototype | Provider lock-in and hard testing | Only behind an adapter |
| Skip job status | Less UI work | Users cannot understand slow processing | Never for v1 |
| No source confidence model | Simpler evaluator | Preprints and peer-reviewed papers get blurred | Never for v1 |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenAI web search | Accept answer text without inspecting citations | Require source URLs and stored evidence records. |
| Paper indexes | Search one API only | Query multiple indexes and merge candidates by DOI/arXiv/title. |
| Qdrant | Embed everything without payload metadata | Store payload filters for entity type, source ID, paper ID, claim ID, and date. |
| Neo4j | Store raw text blobs as nodes | Store normalized entities and relationships with links back to Markdown. |
| TikTok | Treat downloader output as stable | Keep adapter replaceable and test with fixtures. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Reprocessing the same paper repeatedly | Slow jobs and high LLM cost | Deduplicate by DOI/arXiv/OpenAlex/Semantic Scholar ID | After repeated videos mention popular papers |
| Embedding whole PDFs as giant chunks | Poor retrieval quality | Chunk by sections/pages with metadata | Immediately on long papers |
| Synchronous processing in request path | Timeout or frozen UI | Use job queue and status polling | First real video submission |
| Uncached web search | High cost and inconsistent results | Cache query, candidate source, and paper metadata records | Repeated checks in same topic |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Unsafe URL fetching | SSRF or unwanted internal network access | Validate domains and fetch through restricted network clients. |
| Storing API keys in Markdown or logs | Credential leak | Use environment secrets and log redaction. |
| Serving downloaded PDFs blindly | Malware/content risk | Store as files, validate MIME/type, avoid inline execution. |
| Trusting transcript text as instructions | Prompt injection | Treat transcript and paper text as untrusted data in prompts. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing only final verdict | User cannot learn or trust the result | Show claims, evidence, labels, and uncertainty. |
| Hiding job progress | User assumes the app is broken | Show pipeline steps and failures. |
| Making the graph decorative | Graph view looks impressive but is useless | Use graph for source trails, entity pages, and relationship search. |
| Rating before enough evidence exists | User overtrusts early scores | Show rating confidence and evidence count. |

## Looks Done But Is Not Checklist

- [ ] **Claim labels:** Every label has at least one cited source record or is marked insufficient evidence.
- [ ] **Paper matching:** Every selected paper has a recorded matching rationale.
- [ ] **Markdown notes:** Notes have stable IDs and backlinks to related entities.
- [ ] **Qdrant index:** Every indexed chunk can be traced back to a Markdown/source record.
- [ ] **Neo4j graph:** Every graph node links back to canonical metadata or Markdown.
- [ ] **Ratings:** Every rating has an auditable input history.

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Hallucinated citations | Phase 4 | Reject reports with uncited labels. |
| Wrong paper matching | Phase 3 | Candidate selection records matching rationale. |
| Preprints treated as final truth | Phase 3 | Source metadata includes source type and status. |
| Knowledge store drift | Phase 1 and Phase 5 | Consistency check across Markdown, Postgres, Qdrant, Neo4j. |
| Platform ingestion risk | Phase 2 | TikTok code exists only inside ingestion adapter. |
| Opaque ratings | Phase 5 | Rating UI shows evidence history and confidence. |

## Sources

- User project brief from 2026-04-18.
- https://platform.openai.com/docs/guides/tools-web-search - web search citations and live access behavior.
- https://developers.tiktok.com/doc/display-api-overview/ - public video metadata API boundaries.
- https://developers.tiktok.com/doc/content-sharing-guidelines/ - platform guideline concerns and audit restrictions.
- https://qdrant.tech/documentation/search/ - search and filtering behavior that requires payload design.
- https://neo4j.com/docs/ - graph modeling and graph-data-science capabilities.

---
*Pitfalls research for: AI research fact checker*
*Researched: 2026-04-18*
