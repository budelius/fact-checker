# Requirements: Fact Checker v1.1

**Defined:** 2026-04-18
**Milestone:** v1.1 Report Generation Responsiveness
**Core Value:** Save time verifying AI research claims while keeping the accumulated evidence and knowledge graph owned by the user or company.

## v1.1 Requirements

v1.1 fixes the remaining product gap in the report-generation path: frontend-triggered report creation can still spend a long time running live ground-truth discovery and paper processing before evidence evaluation. The milestone makes the work asynchronous, bounded, recoverable, and understandable in the UI.

### Report Generation Runtime

- [ ] **RPT-01**: User can start report generation and receive a report job UUID immediately without waiting for ground-truth discovery, paper processing, evaluation, Markdown writing, or indexing to finish.
- [ ] **RPT-02**: System can run ground-truth discovery, paper processing, evidence evaluation, report writing, and indexing as pollable background job stages with persisted status.
- [ ] **RPT-03**: UI-triggered report runs use explicit live paper discovery and processing limits so a normal report request cannot monopolize the request cycle.
- [ ] **RPT-04**: System can reuse existing ground-truth evidence for matching videos, claims, papers, or source chunks before launching live discovery.
- [ ] **RPT-05**: Failed or interrupted report jobs preserve partial ground-truth and evaluation state, then expose safe retry or rerun behavior without duplicating canonical entities.

### Report User Experience

- [ ] **UX-01**: User sees a clear report-generation workspace with separate ingestion, ground-truth, evaluation, report-writing, and indexing states.
- [ ] **UX-02**: User can understand what the system is doing during a long run, including provider/source names, claim counts, paper limits, selected evidence counts, skipped work, and next action.
- [ ] **UX-03**: User can choose between a fast UI run that reuses stored evidence and applies strict live-processing limits, or a full refresh/rerun before starting report generation.
- [ ] **UX-04**: Error states explain whether the failure came from ingestion, ground-truth discovery, provider/network behavior, evaluation validation, Markdown persistence, or indexing, and provide a recoverable next action.
- [ ] **UX-05**: The report panel layout is redesigned so the primary action, progress, generated report, evidence summary, and rerun/version controls are visually clear on desktop and mobile.

### Evidence Integrity and Operations

- [ ] **EVAL-06**: Bounded report generation preserves evidence traceability and labels claims as insufficient evidence when processing limits prevent enough support, rather than implying stronger certainty.
- [ ] **SRC-06**: Report and ground-truth provenance records whether the run used stored evidence, bounded live discovery, bounded paper processing, or full refresh behavior.
- [ ] **OPS-05**: Async report and ground-truth job state survives browser refreshes and local backend restarts in development.
- [ ] **OPS-06**: Tests cover async job lifecycle, polling, bounded processing, stored-evidence reuse, idempotent retry/rerun, error mapping, and responsive report UX states.

## Deferred Requirements

Tracked for future releases, not part of v1.1.

### Deployment and Access Control

- **SEC-01**: User can sign in and access only their own or organization-authorized knowledge workspace.
- **SEC-02**: API routes enforce ownership boundaries for videos, claims, evidence, reports, annotations, ratings, and graph records.
- **DEP-01**: The system has production-like local deployment configuration, health checks, and environment validation.

### Source Policy and Providers

- **POL-01**: User can configure source tiers that include reputable news, blogs, corporate pages, and expert commentary.
- **POL-02**: User can set organization-specific ground-truth policies.
- **PROV-01**: System can run with alternative LLM providers.
- **PROV-02**: System can run with local transcription and embedding models.

### Additional Inputs

- **INP-01**: User can submit public Instagram/Reels links.
- **INP-02**: User can submit links through a chat client.
- **INP-03**: User can submit links through OpenClaw.
- **INP-04**: User can upload video files directly.

## Out of Scope

Explicitly excluded from v1.1 to keep the milestone focused.

| Feature | Reason |
|---------|--------|
| Authentication and multi-user ownership | Important, but the immediate user-facing blocker is report-generation responsiveness and recovery. |
| New ingestion platforms | The current issue exists after ingestion, so adding platforms would increase surface area before the report path is usable. |
| News/blog source tiers | v1.1 keeps papers and preprints as the ground-truth standard while improving how runs are bounded and explained. |
| Real-time or streaming fact checking | Requires a stronger async job model first. |
| Opaque creator reputation scoring | Ratings must remain evidence-state summaries, not hidden trust scores. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RPT-01 | Phase 6 | Planned |
| RPT-02 | Phase 6 | Planned |
| RPT-05 | Phase 6 | Planned |
| OPS-05 | Phase 6 | Planned |
| RPT-03 | Phase 7 | Planned |
| RPT-04 | Phase 7 | Planned |
| EVAL-06 | Phase 7 | Planned |
| SRC-06 | Phase 7 | Planned |
| UX-01 | Phase 8 | Planned |
| UX-02 | Phase 8 | Planned |
| UX-03 | Phase 8 | Planned |
| UX-04 | Phase 8 | Planned |
| UX-05 | Phase 8 | Planned |
| OPS-06 | Phase 9 | Planned |

**Coverage:**
- v1.1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0

---
*Requirements defined: 2026-04-18*
