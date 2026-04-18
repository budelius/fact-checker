# Feature Research

**Domain:** AI research fact checking for creator videos
**Researched:** 2026-04-18
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| URL submission | User needs a low-friction way to start a check. | LOW | Website form is enough for v1. |
| Job status and errors | Ingestion, search, and summarization are long-running. | MEDIUM | Show pending/running/failed/completed states. |
| Transcript extraction | Fact checking starts from claims in the spoken content. | MEDIUM | Prefer source captions; fall back to transcription. |
| Claim extraction | Reports need atomic claims, not one vague video verdict. | MEDIUM | Preserve timestamps and transcript snippets. |
| Paper/preprint discovery | Ground truth must come from research sources. | HIGH | Combine live web search with OpenAlex, Semantic Scholar, and arXiv. |
| Paper metadata and PDF processing | Evidence must be inspectable and reusable. | HIGH | Store metadata, links, chunks, summaries, and references. |
| Claim-level evidence labels | Users need useful uncertainty, not binary truth. | HIGH | Use supported, contradicted, mixed, insufficient evidence. |
| Markdown output | The owned knowledge base is the product's core memory. | MEDIUM | Create notes for videos, claims, papers, authors, creators, and reports. |
| Vector indexing | Future fact checks need retrieval over prior evidence. | MEDIUM | Index chunks and note summaries in Qdrant. |
| Knowledge graph entities | Source and reputation reasoning needs relationships. | HIGH | Model creators, papers, authors, claims, sources, evidence, topics. |
| Markdown browser | User needs to inspect and reuse stored knowledge. | MEDIUM | Obsidian-like UI is part of v1. |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Self-building knowledge graph | Each fact check improves later checks. | HIGH | Main strategic differentiator. |
| Transparent rating history | Creator, author, paper, and source ratings are explainable. | HIGH | Ratings must link to evidence, not opaque model output. |
| Video context screenshots | Claims can be tied to visual context, overlays, or displayed papers. | MEDIUM | Useful for creator videos with paper screenshots or charts. |
| Source disambiguation from creator references | Finds the exact paper discussed in a video. | HIGH | Key challenge for AI research creator content. |
| User/company-owned corpus | Avoids vendor lock-in and preserves institutional memory. | MEDIUM | Markdown plus self-hostable stores. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| One global truth score | Easy to understand. | Hides uncertainty and may overclaim. | Claim-level evidence labels with citations. |
| Auto-punitive creator rankings | Appears useful for trust. | Can become unfair or legally risky. | Transparent evidence-history ratings with explanations. |
| All platforms in v1 | Broader market. | Ingestion complexity overwhelms core proof. | Public TikTok first, add Instagram later. |
| News as equal ground truth | Sometimes papers are not available. | News varies in quality and may paraphrase research poorly. | Add news later as a configurable lower-trust tier. |
| Private or paywalled video ingestion | More complete coverage. | Legal, privacy, and access risks. | Public links only in v1. |

## Feature Dependencies

```
URL submission
    requires -> TikTok ingestion
        requires -> transcript extraction
            requires -> claim extraction
                requires -> source discovery
                    requires -> paper processing
                        requires -> evidence evaluation
                            requires -> Markdown report

Markdown notes -> Qdrant indexing -> semantic search
Markdown notes -> graph entities -> knowledge graph browser and ratings
```

### Dependency Notes

- **Evidence evaluation requires paper processing:** Labels must cite evidence chunks, not just search-result snippets.
- **Ratings require multiple structured entities:** A creator or author rating needs claims, sources, evidence, and history.
- **Knowledge browser requires Markdown conventions:** The UI should read the same notes users can open outside the app.
- **Graph storage requires entity extraction:** The graph is only useful if papers, authors, sources, creators, and claims are normalized.

## MVP Definition

### Launch With (v1)

- [ ] Public TikTok URL submission - validates the first user workflow.
- [ ] Transcript extraction or transcription fallback - required for claim extraction.
- [ ] Claim extraction with timestamps - required for granular fact checks.
- [ ] Paper/preprint discovery - required for research-grounded evidence.
- [ ] Paper Markdown summaries - required for owned source memory.
- [ ] Claim-level evidence labels - required for useful fact checking.
- [ ] Markdown vault generation - required for ownership and future reuse.
- [ ] Qdrant indexing - required for future retrieval.
- [ ] Neo4j graph storage - required for relationship memory.
- [ ] Website report and Markdown browser - required for user inspection.
- [ ] Basic transparent rating records - required to test reputation logic.

### Add After Validation (v1.x)

- [ ] Better paper disambiguation from screenshots and creator captions - add after the baseline works.
- [ ] User correction workflow - add once reports exist and users can identify bad matches.
- [ ] Better graph visualization - add once graph data has enough density.
- [ ] Source-tier configuration - add once paper/preprint-only behavior is understood.

### Future Consideration (v2+)

- [ ] Instagram ingestion - after TikTok path is stable.
- [ ] Chat client and OpenClaw integration - after API and job model are stable.
- [ ] Smart glasses and streaming SDK support - after real-time requirements are clear.
- [ ] Local or EU-only model provider mode - after the core workflow is validated.
- [ ] Meeting assistant use case - separate ingestion and privacy constraints.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| URL submission | HIGH | LOW | P1 |
| Transcript extraction | HIGH | MEDIUM | P1 |
| Claim extraction | HIGH | MEDIUM | P1 |
| Paper discovery | HIGH | HIGH | P1 |
| Evidence labels | HIGH | HIGH | P1 |
| Markdown vault | HIGH | MEDIUM | P1 |
| Qdrant indexing | HIGH | MEDIUM | P1 |
| Neo4j graph storage | HIGH | HIGH | P1 |
| Markdown browser | HIGH | MEDIUM | P1 |
| Creator/source ratings | MEDIUM | HIGH | P2 |
| Screenshot analysis | MEDIUM | MEDIUM | P2 |
| Instagram ingestion | MEDIUM | HIGH | P3 |
| Smart glasses | MEDIUM | HIGH | P3 |

## Sources

- User project brief from 2026-04-18.
- https://platform.openai.com/docs/guides/tools-web-search - live web search with citations and domain filters.
- https://docs.openalex.org/api-entities/works/search-works - paper search capabilities.
- https://www.semanticscholar.org/product/api - academic graph API capabilities.
- https://qdrant.tech/documentation/search/ - vector and hybrid retrieval feature set.
- https://neo4j.com/docs/ - graph and graph-data-science tooling.

---
*Feature research for: AI research fact checker*
*Researched: 2026-04-18*
