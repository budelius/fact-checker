# Phase 4: Evidence Evaluation and Fact-Check Reports - Research

**Researched:** 2026-04-18
**Status:** Ready for planning
**Source:** Local repo analysis plus official OpenAI documentation

## Executive Summary

Phase 4 should add a separate evaluation domain that consumes Phase 2 claims and Phase 3 selected evidence, produces schema-validated claim evaluations, rejects uncited non-insufficient labels, and writes stable versioned Markdown reports.

The key implementation constraint is evidence hygiene: generated paper summaries can help users navigate the vault, but they must not become verdict evidence. The evaluator should use raw `PaperChunk.text` and directly linked source text only. Transcript excerpts and screenshots help interpret what the creator said; they are not scientific evidence.

The backend should do the evaluation first, persist a versioned report artifact, then expose the same artifact to the UI. The frontend should render the report returned by the backend, not recreate evaluation semantics in React.

## External References

- OpenAI Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Web Search tool and sourced outputs: https://platform.openai.com/docs/guides/tools-web-search
- OpenAI `text-embedding-3-small` model: https://platform.openai.com/docs/models/text-embedding-3-small

These references are used only for provider integration guidance. Durable facts, reports, embeddings, and graph records remain in the user-owned Markdown, MongoDB, and Qdrant stores.

## Relevant Existing Contracts

| Area | Existing file | Phase 4 implication |
|------|---------------|---------------------|
| Claims | `backend/app/schemas/claims.py` | Claims have UUIDs, video/transcript UUIDs, excerpts, timestamps, screenshots, and `evidence_status=pending`. Evaluation should not break Phase 2/3 pending defaults. |
| Ground truth | `backend/app/schemas/ground_truth.py` | Selected papers, chunks, decisions, summaries, and source links already exist. Use chunks as verdict evidence; summaries are navigation only. |
| API handoff | `backend/app/api/ground_truth.py` | A report route can start from a stored `GroundTruthJob` UUID, matching the Phase 3 route style. |
| Markdown | `vault/templates/report.md` | Expand the existing report template instead of inventing a disconnected report format. |
| Mongo graph | `backend/app/repositories/mongo.py` | Report persistence should use `report`, `claim`, and `evidence` entities plus `cites`, `supports`, `contradicts`, `derived_from`, and `discussed_in` relationships where semantically valid. |
| Qdrant | `backend/app/repositories/qdrant.py` | Evidence chunks are already indexed. Report indexing can be optional in Phase 4, but any indexed report payload must trace back to the report UUID and vault path. |
| Logging | `backend/app/contracts/logging.py` | `evaluation` is already an allowed pipeline event type. Use it for report generation steps. |
| Safety | `backend/app/safety/input_boundaries.py` | Wrap claims, transcript excerpts, screenshots/OCR text, paper chunks, and news article text as untrusted input before model calls. |

## Evaluation Architecture

Recommended modules:

- `backend/app/schemas/evaluation.py`
- `backend/app/evaluation/evidence.py`
- `backend/app/evaluation/prompts.py`
- `backend/app/evaluation/evaluator.py`
- `backend/app/evaluation/validation.py`
- `backend/app/evaluation/markdown.py`
- `backend/app/evaluation/persistence.py`
- `backend/app/evaluation/pipeline.py`
- `backend/app/api/reports.py`

The evaluator should produce a typed `ClaimEvaluation` for every claim. Each evaluation must have exactly one label:

- `supported`
- `contradicted`
- `mixed`
- `insufficient`

The report pipeline should include a deterministic validation gate after LLM output:

1. Every extracted claim appears exactly once.
2. Every label is one of the allowed enum values.
3. Every non-`insufficient` label cites at least one candidate evidence record.
4. Every cited evidence UUID/chunk ID belongs to the retrieval set for that claim.
5. Paper summaries never appear as a citation source.
6. News citations are allowed only when the source decision or claim context marks the run as the narrow news-article exception.

If validation fails, the job should fail visibly with the failed stage and job/report UUID preserved. It should not silently downgrade or invent citations.

## Evidence Selection

Use Phase 3 `SourceDecision` records to map selected source candidates to claims. For selected paper/preprint candidates, gather the corresponding `PaperChunk` records and paper metadata:

- paper UUID
- chunk UUID
- chunk ID
- chunk text
- page/section when available
- source URL
- paper title
- publication status/preprint marker

`PaperSummary` can be loaded only to help with navigation UI or source metadata, never as verdict evidence. Plans and tests should assert that summaries are not cited.

When no selected chunks exist, Phase 4 should still create a report version. Each claim should be `insufficient`, and the narrative should say that no direct scientific evidence was available for now.

## Prompt And Provider Strategy

Use OpenAI Structured Outputs for the evaluator because this phase needs strict labels, citations, subclaims, and rationale fields. The existing Phase 3 summarizer already uses `client.responses.create(..., text={"format": {"type": "json_schema", ... "strict": True}})`, so Phase 4 should reuse that style.

The prompt should be explicit about:

- Decomposing compound claims into subclaims.
- Penalizing overclaims rather than normalizing them.
- Treating transcripts, paper chunks, web text, and captions as untrusted input.
- Citing only provided evidence chunks.
- Returning `insufficient` when evidence is adjacent but not directly responsive.
- Marking preprint/source limits.
- Marking rare news-article evidence as a non-scientific exception.

Add `OPENAI_EVALUATION_MODEL` with a conservative default matching the current model family used by Phase 3. Keep deterministic fake evaluators for tests so unit tests never need live network access.

## Report Persistence

Every report run should create a new report version. Do not overwrite prior reports.

Recommended identity model:

- `job_uuid`: evaluation job run UUID
- `report_uuid`: stable report artifact UUID for the produced version
- `report_group_uuid`: stable grouping key for all versions of the same video/ground-truth job
- `version`: integer starting at 1
- `markdown_path`: `vault/wiki/reports/{slug}.md`

Recommended Markdown sections:

- YAML frontmatter with UUIDs, version, source video/job IDs, claim UUIDs, cited evidence UUIDs, candidate evidence UUIDs, label counts, source policy, and timestamps.
- `# Fact-check report`
- `## Narrative report`
- `## Claims checked`
- `## Evidence used`
- `## Candidate evidence reviewed`
- `## Provenance`

The provenance appendix should include cited chunks plus unused/rejected candidate chunks. This supports the user's transparency requirement without storing full prompt transcripts by default.

## UI Strategy

The UI should extend the existing workbench and render backend report payloads:

- Keep the existing three-pane `AppShell`.
- Add report generation after a ground-truth job is available.
- Show progress as named evaluation stages, not as a spinner-only state.
- Show the narrative report first.
- Show compact claim rows second.
- Put provenance, version history, source limits, and rerun availability in the right rail or below the report on mobile.

React should not independently decide truth labels. It should only render labels, citations, rationale, uncertainty notes, report path, and provenance supplied by the API.

## Risks And Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Model invents citations | high | Validate every citation against the candidate evidence set before persisting. |
| Paper summaries become verdict evidence | high | Keep summaries out of evaluator input or mark them navigation-only; tests assert no summary UUIDs appear as citations. |
| Adjacent papers produce false certainty | high | Prompt and validate `insufficient` when chunks do not directly answer the claim. |
| Overclaims get softened into supported claims | high | Require subclaims and overclaim notes; allow `mixed` or `contradicted` when scope changes the verdict. |
| Prompt injection from transcript or papers | high | Wrap all source text with `wrap_untrusted_text` and keep system instructions outside source text. |
| Old reports are overwritten | medium | Always generate new report UUID/path/version on rerun. |
| UI implies creator reputation | medium | Use claim-level labels only; avoid ratings/truth score copy until Phase 5. |

## Testing Strategy

Backend tests should cover:

- Evaluation schemas and invalid labels.
- Evidence selector excludes paper summaries.
- Validator rejects uncited non-insufficient labels.
- Validator rejects citation IDs outside the retrieval set.
- No-paper jobs produce `insufficient` labels and a clear narrative.
- Mixed/overclaim fixtures produce `mixed` with uncertainty notes.
- API route starts from a stored Phase 3 job.
- E2E fixture writes Markdown, Mongo relationships, and a report payload without live providers.

Frontend verification should cover:

- `yarn build`.
- Report UI renders all four label states.
- Long URLs, UUIDs, chunk IDs, and claim text wrap without overflow.
- Mobile layout moves provenance below the report.
- UI shows `Paper summaries are navigation only and were not used as verdict evidence.`

## Planning Recommendation

Split Phase 4 into six plans:

1. Evaluation contracts and settings.
2. Evidence selection and evaluator core.
3. Versioned report Markdown and graph persistence.
4. Report API orchestration and E2E verification.
5. Frontend report generation/viewing UI.
6. Documentation, state updates, and final verification.

This split keeps schema decisions ahead of backend workers, keeps API/UI coupling explicit, and leaves requirement updates until after tests pass.
