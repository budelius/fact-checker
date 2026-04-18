# Phase 4: Evidence Evaluation and Fact-Check Reports - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 takes extracted video claims from Phase 2 and selected source evidence from Phase 3, evaluates each claim against stored evidence, assigns exactly one claim-level label, and produces a cited fact-check report as Markdown plus a web report page. The phase must preserve evaluation inputs so reports can be rerun as the knowledge base improves.

This phase does not create creator, author, paper, or source ratings, does not create an aggregate truth score for a whole creator or video, and does not build the broader knowledge browser/search/graph UI. Those belong to Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Label Policy And Strictness

- **D-01:** The evaluator should be creative in analysis but conservative in verdicts. It should actively decompose claims, check qualifiers, identify overclaims, and explain why a claim is or is not scientifically grounded.
- **D-02:** A `supported` label can use reasonable support: the paper/source evidence supports the claim's main idea, even if the creator's wording is broader than the paper. The report must still expose important scope and qualifier differences.
- **D-03:** Overclaiming should be penalized. If the paper supports a narrow version but the creator overstates it, the label should become `mixed` or `contradicted`, not silently normalize the claim.
- **D-04:** Compound claims should be decomposed into subclaims. Weak or unsupported subclaims can pull down the final claim label.
- **D-05:** Use `insufficient` when no selected source evidence directly addresses the claim, even if related papers exist.
- **D-06:** Do not use prior generated paper summaries as verdict evidence. Paper summaries can be misleading. Evaluation should use cited source chunks/direct source text and may create only evaluation-specific notes grounded in cited chunks.

### Evidence Selection And Citations

- **D-07:** Default scientific verdict evidence is raw paper chunks or directly extracted paper text only.
- **D-08:** Rare source-policy exception: if the creator is specifically talking about a news article, the evaluator may use that news article as a non-scientific source exception. The report must clearly mark it as non-scientific and not present it as normal research ground truth.
- **D-09:** Paper summaries are navigation aids only. They may help locate likely source sections but must never be cited as evidence.
- **D-10:** Each non-`insufficient` claim should prefer two or more cited chunks when available, but one strong cited chunk is acceptable.
- **D-11:** Screenshots and transcript context are used to interpret what the creator claimed. They are not evidence for the scientific answer.
- **D-12:** Supported, contradicted, and mixed labels must cite stored evidence records and source links. Uncited non-`insufficient` labels are invalid.

### Report Shape And UI Page

- **D-13:** The web report page should open with a readable narrative report first, followed by claim details.
- **D-14:** Claim details should be compact by default: verdict, one or two sentence rationale, and citations.
- **D-15:** Markdown reports should serve both humans and machines: a readable Obsidian-style report body plus structured frontmatter/provenance appendix.
- **D-16:** The UI should show uncertainty notes only for `mixed` or `insufficient` labels. Do not clutter every claim with generic uncertainty text.
- **D-17:** The report should show source limits, preprint status, and news-exception status where relevant to the label or uncertainty.

### Reruns, Versions, And Traceability

- **D-18:** Every rerun creates a new report version. Do not overwrite old report versions.
- **D-19:** Store evaluation inputs, selected chunks, labels, citations, and concise rationale. Full prompt/output transcripts are not required for v1 unless planning finds a compliance or debugging reason.
- **D-20:** Reports should expose the exact evidence retrieval set: cited chunks plus rejected or unused candidate chunks in provenance.
- **D-21:** The UI should show `rerun available` when new papers or chunks appear for the same claim.
- **D-22:** Old reports remain stable historical records. A rerun produces a new version that can be compared against earlier versions.

### the agent's Discretion

- Exact backend module names and route names.
- Exact Pydantic schema field names, as long as labels, citations, source text references, subclaims, rationale, provenance, and report versions are represented.
- Exact LLM prompt structure and JSON schema, as long as untrusted input handling, citation validation, and summary-avoidance rules are explicit.
- Exact report page layout details, as long as the first screen is narrative, claim details are compact, and citations/source limits are visible.
- Exact implementation of `rerun available`, as long as it detects newly available papers/chunks for claims already evaluated.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project And Phase Requirements

- `.planning/PROJECT.md` - Product vision, owned knowledge graph, evidence labels, v1 paper/preprint default, and transparency constraints.
- `.planning/REQUIREMENTS.md` - Phase 4 requirements `EVAL-01` to `EVAL-05` and `UI-02`.
- `.planning/ROADMAP.md` - Phase 4 goal, success criteria, implementation notes, and boundaries against Phase 5 ratings/browser work.
- `.planning/STATE.md` - Current project status and Phase 3 handoff.

### Prior Phase Context

- `.planning/phases/01-foundation-and-knowledge-store-contracts/01-CONTEXT.md` - UUID identity, Markdown vault, MongoDB relationship model, Qdrant traceability, and provider boundary decisions.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md` - Claim extraction, transcript/screenshot context, research-basis triage, and UI progress decisions.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-UI-SPEC.md` - Existing workbench visual language and frontend interaction constraints to carry into the report UI.
- `.planning/phases/03-ground-truth-discovery-and-paper-processing/03-CONTEXT.md` - Paper/preprint acceptance policy, selected/rejected source decisions, paper chunk traceability, and Phase 4 boundary.

### Existing Docs And Vault Contracts

- `docs/phase-1-contracts.md` - UUID, Markdown, MongoDB, Qdrant, logging, and untrusted input contracts.
- `docs/phase-2-ingestion.md` - Ingestion routes, artifacts, claims, screenshots, and source-candidate handoff.
- `docs/phase-3-ground-truth.md` - Ground-truth routes, paper policy, processing, Markdown output, storage, indexing, and traceability.
- `vault/SCHEMA.md` - Canonical vault folders, report folder, required frontmatter, relationship conventions, and safety rules.
- `vault/templates/report.md` - Starting report Markdown template to expand for Phase 4.

### Existing Code Contracts

- `backend/app/schemas/claims.py` - Current claim schema and `EvidenceStatus.pending` that Phase 4 must extend or map from.
- `backend/app/schemas/ground_truth.py` - Ground-truth job, paper metadata, paper chunks, summaries, and source decisions from Phase 3.
- `backend/app/schemas/entities.py` - Canonical entity types including `claim`, `evidence`, and `report`.
- `backend/app/schemas/relationships.py` - Existing relationship types including `supports`, `contradicts`, `cites`, `derived_from`, and `discussed_in`.
- `backend/app/schemas/vector_payloads.py` - Qdrant payload trace fields for chunks and relationships.
- `backend/app/api/ground_truth.py` - API route that starts and fetches Phase 3 ground-truth jobs.
- `backend/app/ground_truth/pipeline.py` - Existing handoff from ingestion to selected papers/chunks/summaries.
- `backend/app/repositories/mongo.py` - MongoDB entity/relationship upsert boundary.
- `backend/app/repositories/qdrant.py` - Qdrant deterministic point ID and payload upsert boundary.

### Frontend Contracts

- `frontend/src/components/AppShell.tsx` - Existing three-pane shell where the report page/workbench should fit.
- `frontend/src/components/IngestionWorkbench.tsx` - Current ingestion output view and likely place to attach report generation/display.
- `frontend/src/api/ingestion.ts` - Current API client pattern and frontend types for jobs, claims, screenshots, and transcript context.
- `frontend/src/styles/app.css` - Existing dense workbench styling and responsive layout.
- `frontend/src/styles/tokens.css` - Existing color, spacing, font, rail width, and accent tokens.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/schemas/claims.py`: Claim records already include UUIDs, transcript excerpts, screenshot UUIDs, timestamps, and `evidence_status: pending`.
- `backend/app/schemas/ground_truth.py`: Phase 3 already provides `GroundTruthJob`, `PaperChunk`, `PaperMetadata`, `PaperSummary`, and `SourceDecision`.
- `backend/app/schemas/relationships.py`: `supports` and `contradicts` already exist and should be used for claim-to-evidence relationships. `mixed` and `insufficient` may require additional schema handling or provenance fields rather than direct relationship types.
- `backend/app/repositories/mongo.py`: Existing entity and relationship upsert methods are the persistence boundary for report entities and evaluation relationships.
- `backend/app/repositories/qdrant.py` and `backend/app/schemas/vector_payloads.py`: Existing vector payloads can trace evidence chunks back to source UUIDs, chunk IDs, vault paths, and relationship UUIDs.
- `vault/templates/report.md`: Minimal report template exists and should be expanded rather than replaced with a disconnected format.
- `frontend/src/components/IngestionWorkbench.tsx`: Current workbench already displays job status, claims, transcript, research basis, and screenshots. Phase 4 can attach report actions and report output to this flow.

### Established Patterns

- Backend code uses Python/FastAPI, Pydantic schemas, direct service modules, and test-time dependency overrides.
- UUIDs are canonical identity across Markdown, MongoDB, Qdrant, and API payloads.
- Markdown is the owned human-readable layer; MongoDB and Qdrant must remain traceable to Markdown/source artifacts.
- External source text is untrusted and must not be allowed to steer the evaluator outside the intended instructions.
- Existing frontend uses a dense three-pane workbench, not a landing page.

### Integration Points

- Phase 4 should start from an ingestion job and/or Phase 3 ground-truth job, then produce a report job or report artifact.
- Evaluation should consume original claims, transcript excerpts, screenshot refs, selected paper chunks, source decisions, and source links.
- Reports should write `report` entities under `vault/wiki/reports/`, MongoDB entities/relationships, and API payloads for the frontend.
- UI should surface the report after ingestion/ground-truth completion and provide a rerun path when new evidence appears.

</code_context>

<specifics>
## Specific Ideas

- "Be creative" means the evaluator should inspect the claim deeply: decompose, check exact wording, identify scope mismatch, and catch overclaims.
- Prior paper summaries are misleading and should not be trusted as verdict evidence.
- The source text itself is the anchor: cite chunks/direct text, not generated paper summaries.
- A rare news exception is allowed only when the creator is specifically talking about a news article, and must be marked as non-scientific evidence.
- The report should read like a useful narrative first, with compact claim details and citations after.
- The UI should show when rerunning is available because the knowledge base has new papers or chunks.

</specifics>

<deferred>
## Deferred Ideas

- Creator, paper, author, and source ratings - Phase 5.
- Aggregate creator/video truth scores - out of scope for Phase 4 and discouraged for v1.
- Full knowledge browser, vector search UI, and graph relationship visualization - Phase 5.
- Automatic report reruns when new evidence arrives - not selected. Phase 4 should show `rerun available`; user-triggered rerun creates a new version.
- Treating news as a general ground-truth tier - deferred source-policy work. Phase 4 only allows a narrow non-scientific news exception for claims about news articles.

</deferred>

---

*Phase: 04-evidence-evaluation-and-fact-check-reports*
*Context gathered: 2026-04-18*
