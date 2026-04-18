# Phase 4: Evidence Evaluation and Fact-Check Reports - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 04-evidence-evaluation-and-fact-check-reports
**Areas discussed:** Label Policy And Strictness, Evidence Selection And Citations, Report Shape And UI Page, Reruns, Versions, And Traceability

---

## Label Policy And Strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Direct support only | The paper must clearly support the exact claim, including scope and qualifiers. | |
| Reasonable support | The paper supports the claim's main idea, even if wording is broader than the paper. | yes |
| Generous support | If the claim is directionally aligned with the paper, mark supported. | |

**User's choice:** Reasonable support.
**Notes:** The evaluator should be creative in analysis but not generous in verdicts.

| Option | Description | Selected |
|--------|-------------|----------|
| Penalize overclaiming | If the paper supports a narrow version but the creator overstates it, use mixed or contradicted. | yes |
| Normalize the claim | Silently rewrite it to the scientifically defensible version, then evaluate. | |
| Show both | Evaluate the literal claim and include a charitable version in the report. | |

**User's choice:** Penalize overclaiming.
**Notes:** Do not silently clean up creator claims.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, decompose | Break claims into subclaims and let weak unsupported parts influence the final label. | yes |
| Only for long claims | Decompose only long or compound claims. | |
| No decomposition | Evaluate each extracted claim as one unit. | |

**User's choice:** Yes, decompose.
**Notes:** Subclaim-level weakness can affect the final label.

| Option | Description | Selected |
|--------|-------------|----------|
| No direct paper addresses it | Use insufficient when no selected paper addresses the claim directly. | yes |
| Weak or ambiguous evidence | Use insufficient when evidence exists but is too weak or ambiguous. | |
| Either case | Distinguish not found from found but weak. | |

**User's choice:** No selected paper/source evidence directly addresses the claim.
**Notes:** Related papers alone are not enough.

| Option | Description | Selected |
|--------|-------------|----------|
| Freeform decision | Prior generated paper summaries should not be trusted as verdict evidence. | yes |

**User's choice:** Use own chunk-grounded evaluation; paper summaries are misleading.
**Notes:** Prior paper summaries may be used at most for navigation.

---

## Evidence Selection And Citations

| Option | Description | Selected |
|--------|-------------|----------|
| Only paper chunks | Only paper chunks or directly extracted paper text count as verdict evidence. | yes |
| Chunks plus abstract | Paper chunks plus abstract count as evidence. | |
| Chunks plus notes | Paper chunks, abstract, and evaluator-created chunk-grounded notes count as evidence. | |

**User's choice:** Only raw chunks/direct paper text by default.
**Notes:** Rare exception: if the creator is specifically talking about a news article, use the news article as a non-scientific source exception.

| Option | Description | Selected |
|--------|-------------|----------|
| Navigation only | Paper summaries help find sections but are never cited. | yes |
| Secondary context | Summaries are allowed in reasoning but not citation. | |
| Not used | Summaries are not used during evaluation. | |

**User's choice:** Navigation only.
**Notes:** Paper summaries must not become cited evidence.

| Option | Description | Selected |
|--------|-------------|----------|
| At least one chunk | Each non-insufficient label needs at least one cited chunk. | |
| Prefer 2+ chunks | Prefer two or more chunks when available, but allow one strong chunk. | yes |
| Require multiple chunks | Require multiple chunks for every non-insufficient label. | |

**User's choice:** Prefer 2+ chunks, allow one strong chunk.
**Notes:** Citation validation should reject uncited non-insufficient labels.

| Option | Description | Selected |
|--------|-------------|----------|
| Interpret claim only | Screenshots/transcript help understand what the creator claimed, not prove the science. | yes |
| Influence confidence | They can influence confidence when paper evidence is ambiguous. | |
| Display only | They are displayed only and not used by the evaluator. | |

**User's choice:** Interpret claim only.
**Notes:** Scientific answer must come from source evidence, not video context.

---

## Report Shape And UI Page

| Option | Description | Selected |
|--------|-------------|----------|
| Claim table first | Claim-by-claim table with label, reason, citations, and uncertainty. | |
| Narrative first | Readable executive summary, then claim details. | yes |
| Evidence first | Papers and chunks first, then claims. | |

**User's choice:** Narrative report first.
**Notes:** The report should be useful to read, not just a verdict table.

| Option | Description | Selected |
|--------|-------------|----------|
| Compact | Verdict, 1-2 sentence rationale, and citations. | yes |
| Expanded | Subclaims, overclaim analysis, snippets, and uncertainty by default. | |
| Collapsed | Claim details collapsed by default and expandable. | |

**User's choice:** Compact by default.
**Notes:** Detailed provenance still exists, but the main view stays readable.

| Option | Description | Selected |
|--------|-------------|----------|
| Human-readable note | Obsidian note with sections and wiki links. | |
| Machine audit log | Exhaustive structured details. | |
| Both | Human-readable report plus structured frontmatter/provenance appendix. | yes |

**User's choice:** Both.
**Notes:** Markdown should remain readable while preserving audit structure.

| Option | Description | Selected |
|--------|-------------|----------|
| Every claim | Explicit uncertainty note on every claim. | |
| Mixed or insufficient only | Show uncertainty only when label is mixed or insufficient. | yes |
| Badges plus text | Show uncertainty, limits, and status as visible badges plus text. | |

**User's choice:** Mixed or insufficient only.
**Notes:** Avoid cluttering clear supported/contradicted claims with generic uncertainty text.

---

## Reruns, Versions, And Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| New version every time | Create a new report version for every rerun. | yes |
| Update in place | Update the same report in place with a new timestamp. | |
| Drafts in place | Update drafts in place; create versions once published. | |

**User's choice:** New report version every time.
**Notes:** Auditability is the priority.

| Option | Description | Selected |
|--------|-------------|----------|
| Concise trace | Store inputs, selected chunks, labels, citations, and concise rationale. | yes |
| Full transcripts | Store full prompt/output transcripts too. | |
| Minimal report | Store minimal public report only. | |

**User's choice:** Concise trace.
**Notes:** Enough trace to reproduce the evaluation without storing full LLM transcripts by default.

| Option | Description | Selected |
|--------|-------------|----------|
| Exact retrieval set | Show cited chunks plus rejected/unused candidate chunks in provenance. | yes |
| Cited in report, unused in provenance | Show cited chunks only in report, store unused chunks separately. | |
| Cited only | Store only cited chunks. | |

**User's choice:** Exact retrieval set.
**Notes:** The provenance should reveal both used and unused candidate evidence.

| Option | Description | Selected |
|--------|-------------|----------|
| Rerun available | Show rerun available when new papers/chunks appear for the same claim. | yes |
| Auto rerun | Automatically rerun reports when new evidence arrives. | |
| Manual stable | Keep old reports stable; user triggers rerun manually without availability signal. | |

**User's choice:** Rerun available.
**Notes:** Old reports remain stable; a rerun creates a new version.

---

## the agent's Discretion

- Exact backend module, route, and schema names.
- Exact report page layout details within the narrative-first, compact-claim-detail direction.
- Exact LLM prompt and structured-output schema, subject to citation validation and source-summary constraints.

## Deferred Ideas

- Ratings for creators, papers, authors, and sources.
- Aggregate truth scores.
- Full knowledge browser, search UI, and graph visualization.
- Automatic report reruns.
- General news-as-ground-truth source tiers.
