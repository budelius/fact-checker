# Phase 4 Evidence Evaluation

## Scope

Phase 4 compares extracted video claims against selected evidence from Phase 3 and produces cited, uncertainty-aware fact-check reports. The phase owns evaluation labels, citation validation, Markdown report generation, report versioning, MongoDB relationship writes, and the React report page.

Phase 4 does not create creator, author, paper, or source ratings. It also does not aggregate claim labels into a single truth score. Those features remain Phase 5 work because ratings need accumulated evidence history, transparent confidence, and a browser/search/graph surface.

## API Routes

- `POST /reports/jobs/from-ground-truth/{ground_truth_job_uuid}` starts report generation from a stored Phase 3 ground-truth job.
- `POST /reports/jobs/from-ground-truth/{ground_truth_job_uuid}/rerun` creates a new report version from the same ground-truth job.
- `GET /reports/jobs/{job_uuid}` returns a stored evaluation job or `report_job_not_found`.
- `GET /reports/{report_uuid}` returns a stored report version or `report_not_found`.

The start route returns `ground_truth_job_not_found` when the Phase 3 job is missing, `ingestion_job_not_found` when its linked Phase 2 job is missing, and `ground_truth_job_has_no_claims` when there are no claims to evaluate.

## Labels

Each claim receives exactly one label: supported, contradicted, mixed, or insufficient.

- `supported` means the cited evidence directly supports the claim.
- `contradicted` means the cited evidence directly conflicts with the claim.
- `mixed` means cited evidence supports part of the claim and contradicts, limits, or complicates another part.
- `insufficient` means the available evidence is not enough to assign one of the other labels.

Every non-insufficient label must cite stored evidence records and source links. The validation layer rejects uncited supported, contradicted, and mixed labels.

## Evidence Policy

Verdicts are based on raw evidence text. Paper chunks, direct source text, and explicitly allowed news article text can be evidence. Paper summaries are navigation only and must not be cited as verdict evidence.

The evaluator prompt treats transcripts, paper text, and web content as untrusted input. It instructs the model to ignore instructions inside source material and return only structured JSON that references evidence candidates from the retrieval set.

The validator enforces these boundaries:

- All evaluated claim UUIDs must match the input claim set.
- Every citation must come from the candidate evidence retrieved for that claim.
- `paper_summary` evidence is rejected as a citation source.
- Non-insufficient labels must include citations.
- Insufficient labels must explain the evidence gap.

## No-Paper Behavior

If Phase 3 cannot provide raw paper/preprint evidence for a claim, Phase 4 records the missing-evidence state instead of inventing a truth label. The deterministic fallback produces an insufficient-evidence report with a clear rationale such as "No direct scientific evidence was available for the checked claims for now."

This means the current run found no usable scientific evidence in its selected sources. It does not prove that no evidence exists anywhere.

## Rare News Exception

The v1 default ground-truth policy is still papers and preprints. A rare news exception is allowed only when the claim itself is about a news article or current event rather than scientific evidence. In that case, `news_article` evidence can be rendered and marked with `news_exception`. It must not be presented as scientific ground truth.

## Uncertainty, Preprints, And Source Limits

Reports preserve uncertainty notes, overclaim notes, preprint notes, and source-limit notes from the evaluation output. Mixed and insufficient labels should surface uncertainty directly because the user needs to see why the system did not collapse the result into a simpler label.

Preprints are allowed as v1 ground truth, but reports must expose preprint status so users understand that peer review may be incomplete or absent.

## Markdown Report Format

Markdown reports are written under:

`vault/wiki/reports/`

Each report contains frontmatter with stable UUIDs, report group UUID, version, linked ingestion and ground-truth job UUIDs, claim UUIDs, cited evidence UUIDs, candidate evidence UUIDs, label counts, source policy notes, and timestamps.

The body includes:

1. `# Fact-check report`
2. `## Narrative report`
3. `## Claims checked`
4. `## Evidence used`
5. `## Candidate evidence reviewed`
6. `## Provenance`
7. `### Validation`

The provenance section repeats the summary boundary: summaries are navigation only and were not used as verdict evidence.

## MongoDB Relationships

Report persistence writes a report entity and graph relationships through the MongoDB repository boundary.

- Reports `cites` every cited evidence record.
- Supported claims `supports` their cited evidence.
- Contradicted claims `contradicts` their cited evidence.
- Mixed claims use `cites` relationships with mixed provenance instead of forcing a single support or contradiction edge.
- Insufficient claims are linked as discussed in the report but do not create support or contradiction edges.

This keeps graph edges aligned to what the evidence actually says.

## Versioning And Reruns

Report groups are deterministic for an ingestion job, ground-truth job, and source video. Each run creates a new report UUID and version number within the group.

The React workbench exposes this as `Rerun report`. Reruns do not overwrite earlier reports; they add a new version so changes in retrieved evidence, evaluator behavior, or source policy remain auditable.

Optional report chunk indexing is currently skipped. Paper chunks remain the retrieval base for verdict evidence.

## Frontend Report UI

The report UI lives in the existing React workbench.

- `Generate report` starts Phase 3 ground-truth discovery first when the current ingestion job has no ground-truth job, then starts Phase 4 report generation.
- The completed view renders the narrative report before claim details.
- Claim rows show backend-provided labels, rationales, transcript context, citations, evidence snippets, overclaim notes, source-limit notes, and uncertainty notes.
- The right rail switches to report provenance for the active report and shows report UUIDs, version, Markdown path, label counts, source policy, evidence counts, and validation count.

The UI renders backend report payloads only. It does not compute labels, infer ratings, or create a truth score.

## Verification

```bash
cd backend && uv run pytest tests/test_evaluation_schemas.py tests/test_evaluation_evidence.py tests/test_evaluation_evaluator.py tests/test_evaluation_validation.py tests/test_evaluation_markdown.py tests/test_evaluation_persistence.py tests/test_reports_api.py tests/test_evaluation_e2e.py -q
cd backend && uv run pytest -q
cd frontend && yarn build
cd frontend && yarn tsc --noEmit
```
