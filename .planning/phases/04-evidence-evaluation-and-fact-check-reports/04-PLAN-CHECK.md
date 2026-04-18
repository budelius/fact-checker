# Phase 4 Plan Check

**Checked:** 2026-04-18
**Verdict:** VERIFICATION PASSED
**Mode:** Inline local plan check; no MCP server or subagent used.

## Scope Check

Phase 4 goal:

> Compare each video claim against stored source evidence and produce cited, uncertainty-aware fact-check reports.

The plan set covers this goal through six executable plans:

| Plan | Wave | Dependency | Purpose |
|------|------|------------|---------|
| `04-01-PLAN.md` | 1 | none | Evaluation schemas, labels, report payloads, and settings. |
| `04-02-PLAN.md` | 2 | 01 | Evidence selection, prompt/evaluator boundary, and citation validation. |
| `04-03-PLAN.md` | 2 | 01 | Versioned Markdown reports and MongoDB graph persistence. |
| `04-04-PLAN.md` | 3 | 02, 03 | Evaluation pipeline, reports API, and backend E2E tests. |
| `04-05-PLAN.md` | 4 | 04 | React report generation and report viewing UI. |
| `04-06-PLAN.md` | 5 | 04, 05 | Docs, full verification, requirements/state handoff. |

## Requirement Coverage

| Requirement | Covered by | Notes |
|-------------|------------|-------|
| EVAL-01 | 01, 02, 04, 06 | Claims are loaded, paired with evidence, evaluated once, and verified in E2E tests. |
| EVAL-02 | 01, 02, 04, 06 | `EvaluationLabel` defines exactly supported, contradicted, mixed, insufficient. |
| EVAL-03 | 01, 02, 03, 04, 06 | Citation schemas, validator, persistence, API tests, and docs all enforce cited non-insufficient labels. |
| EVAL-04 | 01, 02, 03, 04, 06 | Report schemas and Markdown require uncertainty, source limits, preprint status, and news-exception notes. |
| EVAL-05 | 03, 04, 06 | Versioned Markdown report generation is planned, persisted, tested, and documented. |
| UI-02 | 05, 06 | Report UI renders claims, labels, evidence, citations, screenshots/timestamps, uncertainty, provenance, versions, and Markdown path. |

## Decision Coverage

| Decision area | Plan coverage |
|---------------|---------------|
| Creative but conservative evaluation | Plan 02 prompt and validation tasks require subclaims, overclaim detection, direct evidence, and conservative labels. |
| Paper summaries are not evidence | Plans 02, 03, 04, 05, and 06 all include explicit summary-exclusion checks/copy/tests. |
| Rare news exception | Plans 01, 02, 03, and 06 include source policy/news-exception metadata and display/documentation. |
| Uncited non-insufficient labels invalid | Plans 02 and 04 make citation validation a hard gate before persistence. |
| Versioned reruns | Plans 03, 04, and 05 require new versions and stable historical reports. |
| Provenance | Plans 01, 03, 04, and 05 require cited and unused candidate evidence in payloads, Markdown, and UI. |
| No ratings/truth scores | Plans 05 and 06 explicitly avoid creator ratings and aggregate truth scores in Phase 4. |

## Dependency Check

The dependency graph is acyclic:

1. Contracts first: `04-01`.
2. Backend core and persistence can run in parallel after contracts: `04-02`, `04-03`.
3. API orchestration waits for core plus persistence: `04-04`.
4. UI waits for API payloads: `04-05`.
5. Documentation and requirement completion wait for backend and frontend verification: `04-06`.

## Validation Run

The local plan-structure validator passed for all executable plans:

- `04-01-PLAN.md`: valid, 3 tasks.
- `04-02-PLAN.md`: valid, 4 tasks.
- `04-03-PLAN.md`: valid, 3 tasks.
- `04-04-PLAN.md`: valid, 3 tasks.
- `04-05-PLAN.md`: valid, 4 tasks.
- `04-06-PLAN.md`: valid, 3 tasks.

Additional scans:

- New planning artifacts contain no non-ASCII characters.
- Requirement IDs appear across the plan set.
- Key risk terms appear across the plan set: paper summaries, insufficient, supported, contradicted, mixed, citations, rerun.

## Residual Risks

| Risk | Handling |
|------|----------|
| Report API shape may need small adjustment during execution | Plan 01 owns schemas first; Plan 04 tests API payloads before frontend work. |
| Frontend currently has no Phase 3 UI trigger | Plan 05 adds a minimal ground-truth API client so `Generate report` can run ground truth before report generation. |
| Mixed claim relationships can be semantically tricky | Plan 03 uses `cites` plus provenance for mixed labels and avoids misleading support/contradict edges. |
| Optional report indexing may be too much for Phase 4 | Plan 04 marks report indexing optional; Markdown/Mongo persistence are required. |

## Gate Result

The Phase 4 plan is executable, requirement-covered, dependency-safe, and aligned with the Phase 4 context and UI contract.
