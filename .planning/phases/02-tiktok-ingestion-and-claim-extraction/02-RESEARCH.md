# Phase 2: TikTok Ingestion and Claim Extraction - Research

**Researched:** 2026-04-18
**Domain:** FastAPI ingestion jobs, compliance-gated TikTok adapter, transcript/keyframe extraction, LLM claim extraction, React progress UI
**Confidence:** MEDIUM
**Network:** Not used by request; external docs are listed as future implementation checks rather than cited sources. [VERIFIED: user prompt]

<user_constraints>
## User Constraints (from CONTEXT.md)

The following locked decisions, discretion areas, and deferred ideas are copied from `02-CONTEXT.md`. [VERIFIED: .planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md]

### Locked Decisions

### Submission and Progress UX

- **D-01:** The frontend should let the user paste a public TikTok URL, submit it, and receive a job UUID.
- **D-02:** The UI must show visible progress and what the backend is actually doing, not only a generic spinner.
- **D-03:** Progress should expose both lifecycle status and current operation, such as validating URL, reading public page transcript, downloading media if allowed, transcribing, capturing screenshots, extracting claims, and checking for research/source references.
- **D-04:** Use the Phase 1 job status language (`pending`, `running`, `failed`, `complete`/`succeeded`) while allowing more detailed stage messages for user-facing progress.
- **D-05:** Failed ingestion and unsupported URLs should produce clear, recoverable states so the user can try another URL or use the fixture/pasted-transcript path.

### TikTok Adapter and Transcript Retrieval

- **D-06:** The primary transcript path should try to retrieve captions/transcript from the public TikTok video page or public video metadata when available.
- **D-07:** If no transcript is available from the public page/captions, the adapter may try to download the public video behind the compliance gate and transcribe it.
- **D-08:** Download/transcription behavior must remain isolated inside the ingestion adapter. Downstream claim extraction should receive normalized transcript/media artifacts and must not depend on TikTok-specific implementation details.
- **D-09:** Keep a fixture or pasted-transcript ingestion path available for tests, development, and cases where live platform access is unavailable.
- **D-10:** The existing `stoz3n-chat-agent` implementation is a concrete reference for `yt-dlp` metadata/subtitle/video download and OpenCV frame extraction patterns, but the Phase 2 implementation must adapt it to this repo's compliance, UUID, logging, untrusted-input, and vault contracts.

### Transcript Provenance

- **D-11:** Store transcript provenance explicitly: retrieval method, source URL, source artifact UUID, timestamps/segments when available, extraction/transcription provider if used, confidence or quality notes, and failure reason when unavailable.
- **D-12:** Transcript text is untrusted external content and must be treated with the Phase 1 untrusted-input boundary before LLM use or Markdown rendering.
- **D-13:** Caption/page transcript, subtitle extraction, transcription fallback, pasted transcript, and test fixture transcript should be distinguishable in stored metadata.

### Visual Context Capture

- **D-14:** Screenshots/keyframes are primarily for memory, review, and later source discovery, not for showing the creator's face or decorative context.
- **D-15:** Prioritize frames that appear to contain paper titles, arXiv/DOI strings, URLs, link lists, slides, screenshots of articles, or other source clues.
- **D-16:** Store a small representative screenshot/keyframe set with UUIDs, timestamps, vault asset paths, and references from claims when relevant.
- **D-17:** The exact screenshot count, selection heuristic, and frame interval are left to planning, but the implementation must support claim-adjacent screenshots and source-clue screenshots.

### Claim Extraction and Research-Basis Triage

- **D-18:** Extract atomic AI research claims from the transcript, not broad summaries. Each claim should be individually checkable later.
- **D-19:** Each extracted claim should include source video UUID, creator UUID if known, timestamp or timestamp range, transcript excerpt, screenshot/keyframe refs when relevant, extraction confidence, and an evidence status that remains pending for later phases.
- **D-20:** Claim context must stay separate from evidence so later paper discovery and evaluation can be rerun without losing the original video-derived claim.
- **D-21:** Extract candidate source references alongside claims: paper-like titles, DOI/arXiv identifiers, URLs, author names, named studies, news/article titles, or explicit "a paper says..." style references.
- **D-22:** If no paper/source candidates can be found from transcript or screenshots, classify the video or claim set as opinion-based, not research-backed, or unratable for now.
- **D-23:** A core value of this phase is to quickly answer whether a TikTok video appears research-based at all, before spending later pipeline effort on full evidence discovery.

### Claude's Discretion

- Exact backend route names, service module names, and MongoDB collection names, as long as they follow Phase 1 UUID and repository/module boundaries.
- Exact progress transport for v1, such as polling, server-sent events, or a simple refresh loop, as long as the user can see meaningful stage updates.
- Exact screenshot/keyframe selection algorithm, as long as it prioritizes source clues and claim context.
- Exact field names for research-basis status, as long as the states distinguish source candidates found, no research source found, opinion/unratable, and needs manual review.
- Exact LLM prompt wording and JSON schema details, as long as untrusted-input handling and parse-failure behavior are explicit.

### Deferred Ideas (OUT OF SCOPE)

- Full paper discovery, paper downloading, paper indexing, and Markdown paper summaries - Phase 3.
- Comparing claims against papers and judging truthfulness - Phase 4.
- Creator ratings, author ratings, source ratings, knowledge graph browsing, and vector search UI - Phase 5.
- Real-time smart-glasses or meeting-assistant fact checking - future milestone, not v1 Phase 2.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ING-01 | User can submit a public TikTok video URL from a website. [VERIFIED: .planning/REQUIREMENTS.md] | Add a React URL form and a user-owned video upload control inside `AppShell`, call FastAPI submission/upload endpoints, and return a job UUID. [VERIFIED: 02-UI-SPEC.md; user scope correction 2026-04-18] |
| ING-02 | User can see whether a submitted job is pending, running, failed, or complete. [VERIFIED: .planning/REQUIREMENTS.md] | Persist job lifecycle plus per-stage status in MongoDB and expose it through polling; map backend `succeeded` to UI `complete`. [VERIFIED: backend/app/contracts/logging.py; 02-UI-SPEC.md] |
| ING-03 | System can retrieve public TikTok video metadata and media through a compliance-gated ingestion adapter. [VERIFIED: .planning/REQUIREMENTS.md] | Put all `yt-dlp` metadata, subtitle, video download, and compliance-gate logic behind a TikTok adapter. [VERIFIED: 02-CONTEXT.md; stoz3n-chat-agent/src/extraction/video.py] |
| ING-04 | System can retrieve source captions or generate a transcript when captions are unavailable. [VERIFIED: .planning/REQUIREMENTS.md] | Try public captions/subtitles first; use media download plus transcription only when the compliance gate allows it; keep fixture/pasted transcript available. [VERIFIED: 02-CONTEXT.md] |
| ING-05 | System can capture representative screenshots or keyframes for visual context. [VERIFIED: .planning/REQUIREMENTS.md] | Use OpenCV-style keyframe extraction, but prioritize source-clue and claim-adjacent frames rather than generic interval-only sampling. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; 02-CONTEXT.md] |
| CLM-01 | System can extract atomic AI research claims from the video transcript. [VERIFIED: .planning/REQUIREMENTS.md] | Use schema-validated LLM extraction over timestamped transcript segments wrapped as untrusted content. [VERIFIED: backend/app/safety/input_boundaries.py; 02-CONTEXT.md] |
| CLM-02 | Each extracted claim stores source video, timestamp, transcript excerpt, and relevant screenshot reference. [VERIFIED: .planning/REQUIREMENTS.md] | Extend Pydantic schemas and vault/MongoDB write services so claim notes include video UUID, transcript segment UUIDs, timestamp range, excerpt, and screenshot UUIDs. [VERIFIED: backend/app/schemas/entities.py; vault/SCHEMA.md] |
| CLM-03 | System can preserve claim context separately from evidence. [VERIFIED: .planning/REQUIREMENTS.md] | Store `evidence_status: pending` and no evaluation labels in Phase 2; relationship edges should describe derivation from video/transcript/screenshot, not evidence support. [VERIFIED: 02-CONTEXT.md; backend/app/schemas/relationships.py] |
| UI-01 | User can paste a TikTok URL into a web form and start a fact-checking job. [VERIFIED: .planning/REQUIREMENTS.md] | Implement `TikTokSubmissionPanel`, `JobStatusHeader`, `ProgressTimeline`, artifact status, claims, screenshots, and research-basis panels inside the existing shell. [VERIFIED: 02-UI-SPEC.md; frontend/src/components/AppShell.tsx] |
</phase_requirements>

## Summary

Phase 2 should be planned as a normalized ingestion-and-extraction pipeline, not as a TikTok-specific feature scattered across routes, UI components, and claim extraction. [VERIFIED: 02-CONTEXT.md] The backend should create a job UUID, record stage-by-stage progress, retrieve public metadata/captions through an adapter, accept user-owned video uploads into local raw artifact storage, optionally download media only after a compliance gate, normalize transcript and keyframe artifacts, extract atomic claims, triage whether research/source clues exist, and write owned artifacts to the vault and MongoDB conventions from Phase 1. [VERIFIED: docs/phase-1-contracts.md; backend/app/contracts/logging.py; 02-CONTEXT.md; user scope correction 2026-04-18]

The largest planning risk is not the React form; it is preserving traceability while handling unreliable external media. [VERIFIED: .planning/ROADMAP.md; 02-CONTEXT.md] The reference `stoz3n-chat-agent` code proves useful patterns for `yt-dlp` metadata/subtitle/video access, OpenCV frame extraction, duplicate/permanent failure handling, and transcript reference extraction, but it also mixes discovery/evaluation into one flow and its subtitle cleanup discards timestamps, so Phase 2 should adapt only the media/progress ideas. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; stoz3n-chat-agent/src/extraction/queue.py]

**Primary recommendation:** Plan Phase 2 in slices: job/status API, compliance-gated TikTok adapter, transcript provenance, keyframe/source-clue capture, schema-validated claim extraction, research-basis triage, vault/MongoDB persistence, then the UI that renders normalized job state. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]

## Project Constraints (from AGENTS.md)

- Markdown is the canonical human-readable knowledge store. [VERIFIED: AGENTS.md]
- MongoDB is the structured metadata and graph relationship store. [VERIFIED: AGENTS.md]
- Qdrant is the vector database target, but Phase 2 does not need to index vectors unless the planner intentionally includes derived placeholder payloads. [VERIFIED: AGENTS.md; .planning/ROADMAP.md]
- OpenAI APIs are allowed for v1, but durable knowledge must remain outside OpenAI-hosted memory. [VERIFIED: AGENTS.md]
- v1 input is public TikTok links only. [VERIFIED: AGENTS.md]
- v1 ground truth is papers and preprints only; Phase 2 should only triage paper/source candidates, not discover or evaluate them. [VERIFIED: AGENTS.md; 02-CONTEXT.md]
- Fact-check labels are `supported`, `contradicted`, `mixed`, or `insufficient evidence`, but Phase 2 must not assign those labels because evidence evaluation is Phase 4. [VERIFIED: AGENTS.md; .planning/ROADMAP.md; 02-UI-SPEC.md]
- Every label, rating, and report must be traceable to evidence; Phase 2 should maintain traceable claim context so later phases can satisfy that rule. [VERIFIED: AGENTS.md; .planning/REQUIREMENTS.md]
- TikTok ingestion must stay behind a compliance-gated adapter. [VERIFIED: AGENTS.md; 02-CONTEXT.md]
- No `CLAUDE.md` exists in the project root, and `AGENTS.md` is the active project instruction file found in this workspace. [VERIFIED: command `find . -maxdepth 2 -name CLAUDE.md`; command `find . -maxdepth 2 -name AGENTS.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| URL submission | Browser / Client | API / Backend | The React form owns entry and recoverable UI state, while the backend validates and creates the canonical job UUID. [VERIFIED: 02-UI-SPEC.md] |
| Job lifecycle and progress | API / Backend | Database / Storage, Browser / Client | The backend owns truth for lifecycle/stage state; MongoDB persists it; the UI only renders normalized progress. [VERIFIED: backend/app/contracts/logging.py; 02-UI-SPEC.md] |
| TikTok retrieval | API / Backend | External platform adapter | Platform-specific metadata, captions, subtitle, and media behavior must remain inside the ingestion adapter. [VERIFIED: 02-CONTEXT.md] |
| Compliance gate | API / Backend | Configuration | Media download and transcription fallback must be blocked or allowed before any adapter download path runs. [VERIFIED: AGENTS.md; 02-CONTEXT.md] |
| User-owned video upload | Browser / Client, API / Backend | Vault / raw assets | Browser uploads go to this backend and are stored under `vault/raw/videos/` with UUID/provenance metadata; third-party transcription remains explicit config, not implicit upload. [VERIFIED: user scope correction 2026-04-18] |
| Transcript normalization | API / Backend | Database / Storage | Claim extraction needs timestamped normalized transcript segments, not raw VTT/SRT/page text. [VERIFIED: 02-CONTEXT.md; .planning/REQUIREMENTS.md] |
| Keyframe/source-clue capture | API / Backend | Vault / raw assets | Frames are derived from media and stored as UUID-addressed artifacts with timestamps and vault paths. [VERIFIED: 02-CONTEXT.md; vault/SCHEMA.md] |
| Claim extraction | API / Backend | LLM provider | The backend wraps untrusted transcript content, validates structured output, and persists claims; the provider is not a durable store. [VERIFIED: backend/app/safety/input_boundaries.py; AGENTS.md] |
| Research-basis triage | API / Backend | Browser / Client | The backend determines candidate source clues and triage state; the UI must display the panel even when no candidates exist. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md] |
| Vault/MongoDB writes | Database / Storage | API / Backend | UUID identity, Markdown notes, entity documents, and relationships are storage responsibilities invoked by backend services. [VERIFIED: docs/phase-1-contracts.md; backend/app/repositories/mongo.py] |
| Progress UI | Browser / Client | API / Backend | The UI should render lifecycle, current operation, per-stage statuses, artifact statuses, and recoverable errors from normalized job data. [VERIFIED: 02-UI-SPEC.md] |

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard for This Phase |
|----------------|---------|---------|-----------------------------|
| FastAPI | 0.136.0 | HTTP API for submit/status endpoints. [VERIFIED: backend/uv.lock] | Existing backend app uses FastAPI and exposes `/health` and `/contracts`. [VERIFIED: backend/app/main.py] |
| python-multipart | To be added and locked during implementation | Multipart form parsing for `UploadFile` video uploads. [ASSUMED] | FastAPI multipart uploads require this dependency; add only with the upload endpoint implementation. |
| Pydantic | 2.13.2 | Schemas for jobs, artifacts, claims, transcript segments, and triage output. [VERIFIED: backend/uv.lock] | Existing entity, relationship, settings, and payload contracts use Pydantic. [VERIFIED: backend/app/schemas/entities.py; backend/app/schemas/relationships.py] |
| PyMongo | 4.16.0 | Persist jobs, entities, and relationship documents. [VERIFIED: backend/uv.lock] | Phase 1 chose MongoDB as the metadata and relationship store. [VERIFIED: docs/phase-1-contracts.md] |
| python-frontmatter | 1.1.0 | Write Obsidian-compatible Markdown notes with YAML frontmatter. [VERIFIED: backend/uv.lock] | Vault notes require YAML frontmatter with UUID, entity type, slug, relationships, and timestamps. [VERIFIED: vault/SCHEMA.md] |
| React | 19.2.5 | UI shell and Phase 2 ingestion workspace. [VERIFIED: frontend/yarn.lock] | Existing frontend is React/Vite and the approved UI contract extends `AppShell`. [VERIFIED: frontend/src/components/AppShell.tsx; 02-UI-SPEC.md] |
| Vite | 8.0.8 | Frontend build/dev server. [VERIFIED: frontend/yarn.lock] | Existing frontend scripts are Vite-based. [VERIFIED: frontend/package.json] |
| lucide-react | 1.8.0 | Icons for copy, retry, progress, screenshot, and artifact actions. [VERIFIED: frontend/yarn.lock] | UI-SPEC declares lucide-react as the icon library. [VERIFIED: 02-UI-SPEC.md] |
| yt-dlp CLI | 2026.02.04 installed locally | Public metadata, subtitle, and optionally media download adapter operations. [VERIFIED: command `yt-dlp --version`; stoz3n-chat-agent/src/extraction/video.py] | The local reference already uses `yt-dlp --dump-json`, subtitle extraction, and bounded video download. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py] |
| OpenCV / cv2 | 4.13.0 available globally, not installed in backend venv | Keyframe extraction from downloaded media. [VERIFIED: command `python3 -c "import cv2"`; command `backend/.venv/bin/python -c "import cv2"`] | The local reference uses `cv2.VideoCapture` and `cv2.imencode` to extract PNG frames. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| OpenAI Python SDK | Not installed in backend venv | Transcription fallback and LLM extraction/triage. [VERIFIED: command `backend/.venv/bin/python -c "import openai"`] | Use after adding and verifying the dependency, because OpenAI APIs are allowed for v1 but durable outputs must be stored locally. [VERIFIED: AGENTS.md] |
| ffmpeg | 8.0.1 installed locally | Audio extraction or transcoding before transcription. [VERIFIED: command `ffmpeg -version`] | Use only inside the adapter/transcription path and only after compliance allows media download. [VERIFIED: 02-CONTEXT.md] |
| Tesseract CLI | 5.5.1 installed locally | Optional OCR for keyframe source-clue detection. [VERIFIED: command `tesseract --version`] | Use only if the planner accepts the extra dependency; otherwise triage source clues from transcript text and optional vision extraction. [ASSUMED] |
| Pillow / PIL | Not installed in backend venv | Image preprocessing for OCR and thumbnail handling. [VERIFIED: command `backend/.venv/bin/python -c "import PIL"`] | Add only if OCR/preprocessing is included in the Phase 2 plan. [ASSUMED] |
| webvtt/srt parser | Not installed or verified | Timestamp-preserving caption parsing. [VERIFIED: backend/pyproject.toml; user network constraint] | Before implementation, verify a current caption parser package or deliberately implement a narrow, tested parser; the local `_clean_vtt` helper is insufficient because it removes timing. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Polling `GET /ingestion/jobs/{uuid}` | Server-sent events | Polling is enough for v1 visible progress and avoids introducing streaming complexity; SSE can be added if progress feels stale. [ASSUMED] |
| In-process FastAPI background task/worker | Celery/RQ/Redis | The repo has no Redis or worker infrastructure; MongoDB-persisted jobs plus in-process execution is smaller for Phase 2, but restart recovery must mark stale running jobs failed or retryable. [VERIFIED: infra/docker-compose.yml; stoz3n-chat-agent/src/extraction/queue.py] |
| OCR-based frame scoring | LLM vision frame scoring | OCR is more deterministic for DOI/arXiv/URL clues, while vision may better detect screenshots of papers; both need explicit dependency/provider checks before implementation. [ASSUMED] |
| Store full downloaded video | Store only transcript/keyframes and retrieval metadata | Full video storage increases compliance, disk, and privacy risk; Phase 2 only requires visual context and provenance, not a permanent video copy. [VERIFIED: 02-CONTEXT.md; AGENTS.md] |

**Installation guidance:**

```bash
# Backend dependencies to verify and add only if the selected plan needs them.
cd backend
uv add openai opencv-python pillow

# Optional only if OCR is selected.
uv add pytesseract

# Future check before choosing a caption parser.
uv add webvtt-py
```

**Version verification:** Do not lock new package versions from training memory. Network was prohibited for this research, so implementation should verify current versions with `uv add`, lockfile diffs, and official docs before committing dependency changes. [VERIFIED: user prompt]

## Architecture Patterns

### System Architecture Diagram

```text
React URL form
  -> POST /ingestion/tiktok
    -> URL validator and compliance policy
      -> create ingestion job UUID in MongoDB
      -> write pipeline log: ingestion/pending
      -> background ingestion service
        -> TikTok adapter
          -> public metadata/captions path
          -> compliance-gated media download path
            -> transcription fallback
            -> OpenCV keyframe extraction
        -> transcript normalizer with provenance
        -> screenshot/source-clue selector
        -> untrusted-content wrapper
        -> LLM claim extraction with schema validation
        -> research-basis triage
        -> vault writer and MongoDB upserts
        -> relationship writer: claim/video/transcript/screenshot derived_from edges
        -> update job stages and terminal lifecycle status
  -> GET /ingestion/jobs/{job_uuid}
    -> normalized job DTO
      -> ProgressTimeline, ArtifactStatusGrid, TranscriptPreview,
         ScreenshotStrip, ClaimExtractionList, ResearchBasisPanel
```

This flow keeps TikTok-specific retrieval inside the adapter, keeps untrusted transcript/media text out of prompts until wrapped, and keeps durable artifacts in the owned stores. [VERIFIED: 02-CONTEXT.md; backend/app/safety/input_boundaries.py; docs/phase-1-contracts.md]

### Recommended Project Structure

```text
backend/app/
  api/
    ingestion.py              # POST submit, GET job status, fixture/pasted-transcript route
  ingestion/
    jobs.py                   # job lifecycle, stages, stale-job handling
    progress.py               # pipeline log event helper and MongoDB progress records
    compliance.py             # media download policy and compliance result
    adapters/
      tiktok.py               # public TikTok metadata/captions/media adapter
      fixture.py              # fixture and pasted-transcript ingestion path
    transcript.py             # timestamped segment model and provenance normalization
    keyframes.py              # OpenCV extraction and source-clue scoring
    claims.py                 # untrusted wrapping, LLM call, parse validation
    research_basis.py         # DOI/arXiv/URL/title/source-candidate triage
    persistence.py            # vault/MongoDB entity and relationship writes
  schemas/
    ingestion.py              # job, stage, artifact, transcript, screenshot DTOs
    claims.py                 # claim extraction DTOs and evidence_status=pending

frontend/src/
  api/
    ingestion.ts              # typed submit/status calls
  components/ingestion/
    TikTokSubmissionPanel.tsx
    JobStatusHeader.tsx
    ProgressTimeline.tsx
    ArtifactStatusGrid.tsx
    TranscriptPreview.tsx
    ScreenshotStrip.tsx
    ClaimExtractionList.tsx
    ResearchBasisPanel.tsx
    RecoverableError.tsx
```

The structure follows Phase 1's backend/frontend split and keeps external calls in obvious modules. [VERIFIED: 01-CONTEXT.md; frontend/src/components/AppShell.tsx; backend/app/repositories/mongo.py]

### Pattern 1: Job and Stage State Are Separate

**What:** Store a top-level lifecycle status (`pending`, `running`, `failed`, `succeeded`/`complete`) plus a stage list with stage names, statuses, messages, artifact UUIDs, timestamps, and failure details. [VERIFIED: backend/app/contracts/logging.py; 02-UI-SPEC.md]

**When to use:** Use for every submitted URL and fixture/pasted-transcript ingestion path. [VERIFIED: 02-CONTEXT.md]

**Planner note:** The Phase 1 logging contract allows statuses `pending`, `running`, `succeeded`, `failed`, and `skipped`; the UI contract allows per-step `complete`, so the API should either return `succeeded` raw plus a display status or normalize to `complete` at the frontend boundary. [VERIFIED: backend/app/contracts/logging.py; 02-UI-SPEC.md]

### Pattern 2: Compliance Gate Before Download

**What:** The adapter should return a media retrieval artifact with fields like `compliance_allowed`, `policy_reason`, `download_attempted`, `media_artifact_uuid`, and `failure_reason`, even when download is skipped. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]

**When to use:** Use before any `yt-dlp` download, ffmpeg extraction, or transcription fallback that depends on video bytes. [VERIFIED: 02-CONTEXT.md; stoz3n-chat-agent/src/extraction/video.py]

**Planner note:** Default the plan to a blocked/skipped media download path unless a compliance approval flag/config is explicitly set. [VERIFIED: AGENTS.md]

### Pattern 3: Transcript Provenance Is a First-Class Artifact

**What:** Model transcript artifacts with `uuid`, `source_video_uuid`, `method`, `source_url`, `source_artifact_uuid`, `provider`, `segments`, `quality_notes`, `failure_reason`, `created_at`, and `vault_path`. [VERIFIED: 02-CONTEXT.md]

**When to use:** Use for page captions, downloaded subtitles, transcription fallback, pasted transcript, and fixtures. [VERIFIED: 02-CONTEXT.md]

**Planner note:** The local reference `_clean_vtt()` returns plain text and removes timing lines, so Phase 2 must preserve cue timing before claim extraction. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py]

### Pattern 4: Claim Context Is Not Evidence

**What:** Store extracted claims as video-derived context with `evidence_status: pending`, timestamp range, transcript excerpt, screenshot UUID refs, extraction confidence, and no truth label. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]

**When to use:** Use for every Phase 2 claim entity. [VERIFIED: .planning/REQUIREMENTS.md]

**Planner note:** Relationship records should use existing types such as `derived_from`, `discussed_in`, or `related_to`; `supports` and `contradicts` belong to later evidence evaluation. [VERIFIED: backend/app/schemas/relationships.py; .planning/ROADMAP.md]

### Pattern 5: Research-Basis Triage Before Paper Discovery

**What:** Extract and store candidate source references from transcript text and screenshot/OCR/visual text, then classify the video/claim set as `source_candidates_found`, `no_research_source_found`, `opinion_or_unratable`, or `needs_manual_review`. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]

**When to use:** Run after transcript/keyframe extraction and before terminal job success. [VERIFIED: 02-UI-SPEC.md]

**Planner note:** Do not call paper search APIs or download papers in Phase 2; store candidates for Phase 3. [VERIFIED: .planning/ROADMAP.md]

### Anti-Patterns to Avoid

- **TikTok logic in claim extraction:** Claim extraction should consume normalized transcript/media context, not `yt-dlp` output or TikTok metadata directly. [VERIFIED: 02-CONTEXT.md]
- **Generic spinner-only progress:** UI must show current operation and stage statuses. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]
- **Plain transcript-only claims with no timestamps:** CLM-02 requires timestamp and excerpt linkage. [VERIFIED: .planning/REQUIREMENTS.md]
- **Raw HTML rendering:** Public-page metadata, captions, OCR, and transcripts are untrusted external content and must render as plain text only. [VERIFIED: backend/app/safety/input_boundaries.py; 02-UI-SPEC.md]
- **Evaluation in Phase 2:** The reference queue verifies against papers, but Phase 2 must stop at claim extraction and research-basis triage. [VERIFIED: stoz3n-chat-agent/src/extraction/queue.py; .planning/ROADMAP.md]
- **UUIDs in filenames:** Vault filenames use readable slugs; UUIDs live in frontmatter. [VERIFIED: docs/phase-1-contracts.md; vault/SCHEMA.md]

## Recommended Implementation Slices

| Slice | Goal | Likely Files |
|-------|------|--------------|
| 1. Schemas and contracts | Add ingestion job, stage, artifact, transcript segment, screenshot, claim, and research-basis DTOs. [VERIFIED: backend/app/schemas/entities.py] | `backend/app/schemas/ingestion.py`, `backend/app/schemas/claims.py`, `backend/tests/test_ingestion_schemas.py` |
| 2. Job API and persistence | Create `POST /ingestion/tiktok`, fixture/pasted transcript endpoint, and `GET /ingestion/jobs/{uuid}`. [VERIFIED: .planning/REQUIREMENTS.md; 02-UI-SPEC.md] | `backend/app/main.py`, `backend/app/api/ingestion.py`, `backend/app/ingestion/jobs.py`, backend tests |
| 3. Progress logging | Persist stage events and current operation using the Phase 1 logging contract. [VERIFIED: backend/app/contracts/logging.py] | `backend/app/ingestion/progress.py`, `backend/tests/test_ingestion_progress.py` |
| 4. Compliance-gated adapter | Implement URL validation, public metadata/caption path, download policy, and adapter result normalization. [VERIFIED: 02-CONTEXT.md; stoz3n-chat-agent/src/extraction/video.py] | `backend/app/ingestion/compliance.py`, `backend/app/ingestion/adapters/tiktok.py`, fixture tests |
| 5. Transcript and keyframes | Preserve timestamped transcript segments and capture source-clue/claim-adjacent frames. [VERIFIED: 02-CONTEXT.md; stoz3n-chat-agent/src/extraction/video.py] | `backend/app/ingestion/transcript.py`, `backend/app/ingestion/keyframes.py`, fixture assets/tests |
| 6. Claim extraction and triage | Wrap untrusted content, call LLM extraction, validate output, and create research-basis state without paper discovery. [VERIFIED: backend/app/safety/input_boundaries.py; 02-CONTEXT.md] | `backend/app/ingestion/claims.py`, `backend/app/ingestion/research_basis.py`, parse-failure tests |
| 7. Vault/Mongo persistence | Write video, creator, transcript/screenshot artifacts, claims, and relationships with UUIDs and slug-only paths. [VERIFIED: vault/SCHEMA.md; backend/app/repositories/mongo.py] | `backend/app/ingestion/persistence.py`, `backend/app/contracts/vault.py`, vault fixture tests |
| 8. React ingestion UI | Extend the existing shell with URL submission, progress timeline, artifacts, transcript, screenshots, claims, triage, and recoverable errors. [VERIFIED: 02-UI-SPEC.md] | `frontend/src/components/AppShell.tsx`, `frontend/src/api/ingestion.ts`, `frontend/src/components/ingestion/*`, CSS files |

## Files Likely Modified

- `backend/pyproject.toml` and `backend/uv.lock` if the plan adds OpenAI, OpenCV, OCR, or caption parser dependencies. [VERIFIED: backend/pyproject.toml; backend/uv.lock]
- `backend/app/main.py` to include the ingestion router. [VERIFIED: backend/app/main.py]
- `backend/app/settings.py` for compliance/download/transcription/provider flags. [VERIFIED: backend/app/settings.py]
- `backend/app/contracts/logging.py` only if the planner decides additional event metadata is necessary; existing statuses already cover Phase 2 stage progress. [VERIFIED: backend/app/contracts/logging.py]
- `backend/app/contracts/vault.py` may need transcript/screenshot path support because entity types include `transcript` and `screenshot` but current wiki folders omit them. [VERIFIED: backend/app/schemas/entities.py; backend/app/contracts/vault.py]
- `vault/SCHEMA.md` may need clarification for transcript and screenshot artifact storage. [VERIFIED: vault/SCHEMA.md]
- `frontend/src/components/AppShell.tsx`, `frontend/src/styles/app.css`, and `frontend/src/styles/tokens.css` for the approved UI contract. [VERIFIED: 02-UI-SPEC.md; frontend/src/components/AppShell.tsx]
- Backend and frontend test files for schemas, progress, adapter fixtures, claim parse failures, and UI states. [VERIFIED: backend/tests/test_contracts.py; frontend/package.json]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TikTok metadata/subtitles/media access | A custom scraper spread through services | A single adapter around `yt-dlp` CLI behavior plus fixture/pasted transcript fallback. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; 02-CONTEXT.md] | Platform behavior is brittle and compliance-sensitive, so isolation is the control surface. [VERIFIED: AGENTS.md] |
| Prompt injection filtering | String replace or "ignore instructions" prompt only | `wrap_untrusted_text()` plus schema validation and plain-text rendering. [VERIFIED: backend/app/safety/input_boundaries.py; 02-UI-SPEC.md] | Transcript, captions, page metadata, OCR, and comments are untrusted external content. [VERIFIED: docs/phase-1-contracts.md] |
| UUID/idempotency | Slug or URL as primary key | UUID as canonical ID and external IDs as aliases. [VERIFIED: docs/phase-1-contracts.md; backend/app/schemas/entities.py] | TikTok URLs/usernames can change or alias, while UUIDs connect Markdown, MongoDB, and Qdrant. [VERIFIED: vault/SCHEMA.md] |
| Caption timing | Plain text cleanup that drops timestamps | Timestamp-preserving caption/subtitle parser with tests; verify package/docs before adding dependency. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; user prompt] | CLM-02 requires timestamps and transcript excerpts. [VERIFIED: .planning/REQUIREMENTS.md] |
| Media source clue detection | Manual frame picking only | OpenCV frame extraction plus deterministic clue signals such as DOI/arXiv/URL/title regex over transcript/OCR/visual text. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; 02-CONTEXT.md] | Phase 2 explicitly prioritizes source-clue screenshots. [VERIFIED: 02-CONTEXT.md] |
| LLM JSON parsing | Trust raw model text | Pydantic-validated DTOs, strict parse failure state, and no fabricated claims. [VERIFIED: backend/app/schemas/entities.py; 02-UI-SPEC.md] | The UI must show parse failure and keep transcript artifacts visible. [VERIFIED: 02-UI-SPEC.md] |
| Paper discovery | Custom source search inside Phase 2 | Store research-basis candidates only; Phase 3 owns full discovery. [VERIFIED: .planning/ROADMAP.md; 02-CONTEXT.md] | Keeping boundaries prevents premature evidence claims and duplicated source logic. [VERIFIED: .planning/ROADMAP.md] |

**Key insight:** The hard part is not downloading a video; it is preserving a traceable chain from public URL to transcript segment to screenshot/keyframe to atomic claim while treating all external text as untrusted. [VERIFIED: .planning/REQUIREMENTS.md; backend/app/safety/input_boundaries.py; docs/phase-1-contracts.md]

## Common Pitfalls

### Pitfall 1: Losing Transcript Timing

**What goes wrong:** Captions are cleaned into a single text blob, so extracted claims cannot point back to a timestamp. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py]

**Why it happens:** The local reference `_clean_vtt()` intentionally strips timing lines and tags. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py]

**How to avoid:** Preserve segment start/end times in the transcript artifact before any LLM call. [VERIFIED: .planning/REQUIREMENTS.md]

**Warning signs:** Claims have excerpt text but no segment UUID or timestamp range. [VERIFIED: .planning/REQUIREMENTS.md]

### Pitfall 2: Bypassing the Compliance Gate

**What goes wrong:** A fallback path downloads public media whenever captions are unavailable. [VERIFIED: 02-CONTEXT.md]

**Why it happens:** The reference code downloads video bytes directly for video jobs. [VERIFIED: stoz3n-chat-agent/src/extraction/queue.py]

**How to avoid:** Gate download before `yt-dlp` media calls and store skipped/blocked media retrieval as an explicit artifact state. [VERIFIED: AGENTS.md; 02-UI-SPEC.md]

**Warning signs:** Transcription fallback runs without a logged `compliance_allowed` decision. [VERIFIED: 02-CONTEXT.md]

### Pitfall 3: Prompt Injection from Transcript or OCR Text

**What goes wrong:** Transcript or OCR text tells the model to ignore instructions or output false claims. [VERIFIED: backend/app/safety/input_boundaries.py]

**Why it happens:** Captions, page metadata, transcript text, and OCR are external content. [VERIFIED: docs/phase-1-contracts.md]

**How to avoid:** Wrap every external text block with `wrap_untrusted_text()`, validate structured output, and never render external HTML. [VERIFIED: backend/app/safety/input_boundaries.py; 02-UI-SPEC.md]

**Warning signs:** Prompts concatenate raw transcript text directly after system instructions. [VERIFIED: backend/app/safety/input_boundaries.py]

### Pitfall 4: Blending Claim Context with Evidence

**What goes wrong:** Extracted claims get premature labels or source matches before Phase 3/4. [VERIFIED: .planning/ROADMAP.md]

**Why it happens:** The reference queue performs transcript reference discovery and paper verification inside the same video flow. [VERIFIED: stoz3n-chat-agent/src/extraction/queue.py]

**How to avoid:** Store source candidates and `evidence_status: pending`; do not run paper discovery, download, or evaluation. [VERIFIED: 02-CONTEXT.md; .planning/ROADMAP.md]

**Warning signs:** UI copy includes "verified", "supported", "contradicted", "true", or "false" on Phase 2 claim rows. [VERIFIED: 02-UI-SPEC.md]

### Pitfall 5: Duplicating Canonical Entities on Rerun

**What goes wrong:** Retrying claim extraction creates duplicate videos, transcripts, screenshots, or claims. [VERIFIED: .planning/REQUIREMENTS.md]

**Why it happens:** URL and slug are tempting keys, but Phase 1 chose UUIDs with external IDs as aliases. [VERIFIED: docs/phase-1-contracts.md]

**How to avoid:** Use deterministic upsert rules around source URL/external video ID aliases and canonical UUIDs; retain the job UUID separately from entity UUIDs. [VERIFIED: docs/phase-1-contracts.md; backend/app/repositories/mongo.py]

**Warning signs:** MongoDB has multiple `video` entities for the same external TikTok video ID without an intentional reprocess lineage. [ASSUMED]

### Pitfall 6: Missing Transcript/Screenshot Vault Contract Gap

**What goes wrong:** The planner assumes transcript and screenshot are wiki note folders, but current vault folder constants omit them. [VERIFIED: backend/app/contracts/vault.py; vault/SCHEMA.md]

**Why it happens:** `EntityType` includes `transcript` and `screenshot`, while `VAULT_WIKI_ENTITY_FOLDERS` lists videos, creators, claims, papers, authors, sources, evidence, reports, and topics. [VERIFIED: backend/app/schemas/entities.py; backend/app/contracts/vault.py]

**How to avoid:** Add an explicit Phase 2 task to decide whether transcripts/screenshots get wiki folders, raw asset paths only, or both; then update contracts/tests consistently. [VERIFIED: vault/SCHEMA.md]

**Warning signs:** Claim rows refer to screenshot UUIDs but no vault path or entity document resolves. [VERIFIED: 02-CONTEXT.md]

## Code Examples

Verified patterns from local sources:

### Stage Progress Event

```python
# Source: backend/app/contracts/logging.py
event = build_pipeline_log_event(
    event_type="ingestion",
    job_uuid=str(job_uuid),
    stage="capture_source_clues",
    status="running",
    message="Capturing frames with paper, DOI, arXiv, URL, or slide clues",
    created_at=now_iso,
    entity_uuid=str(video_uuid),
)
```

Use this pattern for user-visible progress and backend debugging, then persist the current operation in the job document for polling. [VERIFIED: backend/app/contracts/logging.py; 02-UI-SPEC.md]

### Untrusted Transcript Boundary

```python
# Source: backend/app/safety/input_boundaries.py
wrapped_transcript = wrap_untrusted_text(
    label=f"transcript:{transcript_uuid}",
    content="\n".join(segment.text for segment in transcript_segments),
)
```

Use this wrapper before LLM claim extraction, source-candidate triage, OCR-derived text analysis, and any visual-text prompt. [VERIFIED: backend/app/safety/input_boundaries.py; docs/phase-1-contracts.md]

### Claim Extraction DTO Shape

```python
# Source basis: backend/app/schemas/entities.py and 02-CONTEXT.md
class ExtractedClaim(BaseModel):
    uuid: UUID
    source_video_uuid: UUID
    source_transcript_uuid: UUID
    timestamp_start_seconds: float | None = None
    timestamp_end_seconds: float | None = None
    transcript_excerpt: str
    claim_text: str
    screenshot_uuids: list[UUID] = Field(default_factory=list)
    extraction_confidence: float | None = None
    evidence_status: Literal["pending"] = "pending"
```

Keep `evidence_status` locked to `pending` in Phase 2 so later phases can rerun discovery and evaluation without changing original claim context. [VERIFIED: 02-CONTEXT.md; .planning/ROADMAP.md]

### Research-Basis Triage DTO Shape

```python
# Source basis: 02-CONTEXT.md and 02-UI-SPEC.md
class ResearchBasisCandidate(BaseModel):
    candidate_type: Literal["doi", "arxiv", "url", "paper_title", "named_study", "author", "article_title"]
    value: str
    source: Literal["transcript", "screenshot", "metadata"]
    transcript_segment_uuid: UUID | None = None
    screenshot_uuid: UUID | None = None
    confidence: float | None = None


class ResearchBasisTriage(BaseModel):
    status: Literal[
        "source_candidates_found",
        "no_research_source_found",
        "opinion_or_unratable",
        "needs_manual_review",
    ]
    candidates: list[ResearchBasisCandidate] = Field(default_factory=list)
    notes: str | None = None
```

This is triage only; it does not assert that papers exist or that any claim is true. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]

### Timestamp-Preserving Caption Adapter Result

```python
# Source basis: stoz3n-chat-agent/src/extraction/video.py and 02-CONTEXT.md
class TranscriptSegment(BaseModel):
    uuid: UUID
    start_seconds: float | None
    end_seconds: float | None
    text: str
    retrieval_method: Literal["public_caption", "subtitle_file", "transcription", "pasted", "fixture"]
```

Do not reuse `_clean_vtt()` as-is because it returns a deduplicated plain-text string and discards cue timing. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py]

## State of the Art

Because network access was prohibited, this section records current project-local state rather than current external ecosystem claims. [VERIFIED: user prompt]

| Old / Reference Approach | Current Phase 2 Approach | Why It Matters |
|--------------------------|--------------------------|----------------|
| Reference queue downloads video, extracts transcript, searches references, stores document, generates summary, and verifies against papers in one flow. [VERIFIED: stoz3n-chat-agent/src/extraction/queue.py] | Phase 2 should stop at normalized ingestion, claims, source candidates, and owned artifact writes. [VERIFIED: .planning/ROADMAP.md] | Prevents scope creep into Phase 3 discovery and Phase 4 evaluation. [VERIFIED: .planning/ROADMAP.md] |
| Reference subtitle cleanup produces plain text. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py] | Phase 2 needs timestamped segments and transcript provenance. [VERIFIED: .planning/REQUIREMENTS.md; 02-CONTEXT.md] | Claim rows need timestamp/excerpt traceability. [VERIFIED: .planning/REQUIREMENTS.md] |
| Reference frame extraction samples frames by interval. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py] | Phase 2 should support source-clue and claim-adjacent screenshots. [VERIFIED: 02-CONTEXT.md] | Screenshots must help source discovery and memory, not decorative display. [VERIFIED: 02-CONTEXT.md] |
| Phase 1 UI is a static vault browser. [VERIFIED: frontend/src/components/AppShell.tsx] | Phase 2 UI becomes an ingestion workbench inside the existing shell. [VERIFIED: 02-UI-SPEC.md] | The first viewport must show URL submission and current/empty job state. [VERIFIED: 02-UI-SPEC.md] |

**Deprecated/outdated for this phase:**

- The reference `_clean_vtt()` timing-stripping approach is inappropriate for CLM-02 timestamp traceability. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; .planning/REQUIREMENTS.md]
- The reference "verification against discovered papers" flow is out of scope for Phase 2. [VERIFIED: stoz3n-chat-agent/src/extraction/queue.py; .planning/ROADMAP.md]
- Rendering any external transcript, OCR, or public-page content as HTML is disallowed by the UI and safety contracts. [VERIFIED: 02-UI-SPEC.md; backend/app/safety/input_boundaries.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Polling is enough for v1 progress and SSE can be deferred. | Standard Stack / Alternatives | UI may feel stale during long transcription or media download, requiring a transport change. |
| A2 | An in-process FastAPI worker/background task is sufficient for Phase 2 if jobs are persisted in MongoDB. | Standard Stack / Alternatives | Long-running tasks may be interrupted by server restart; planner must add stale-job handling. |
| A3 | OCR with Tesseract/Pillow is optional for source-clue detection. | Standard Stack / Supporting | Source-clue screenshots may be lower quality if no OCR/vision classifier is included. |
| A4 | A dedicated caption parser such as `webvtt-py` may be appropriate after registry/doc verification. | Standard Stack / Supporting | A hand-built parser may miss cue edge cases or produce bad timestamps. |
| A5 | MongoDB can hold operational `ingestion_jobs` separately from canonical `entities` and `relationships`. | Architecture Patterns | If the project later requires all records in the existing `entities` collection, the job repository design may need refactoring. |
| A6 | Deterministic upsert by external TikTok video ID/source URL can prevent duplicate video entities. | Common Pitfalls | TikTok URL variants may not normalize cleanly, causing duplicate entities or mistaken merges. |

## Open Questions

1. **What exact compliance approval controls media download?**
   - What we know: TikTok download/transcription fallback must stay behind a compliance gate. [VERIFIED: AGENTS.md; 02-CONTEXT.md]
   - What's unclear: The project has no current setting or policy document for enabling media downloads. [VERIFIED: backend/app/settings.py]
   - Recommendation: Plan a default-deny config flag and a test that proves download paths are skipped when the gate is closed. [ASSUMED]

2. **Do transcript and screenshot artifacts become wiki notes, raw files, or both?**
   - What we know: `EntityType` includes `transcript` and `screenshot`, but current vault folder constants omit transcript and screenshot folders. [VERIFIED: backend/app/schemas/entities.py; backend/app/contracts/vault.py]
   - What's unclear: Whether Phase 2 should add `vault/wiki/transcripts/` and `vault/wiki/screenshots/`, or store raw assets under `vault/raw/` and link from video/claim notes. [VERIFIED: vault/SCHEMA.md]
   - Recommendation: Make this a Wave 0 contract task before persistence work. [ASSUMED]

3. **Which LLM/transcription model should Phase 2 use?**
   - What we know: OpenAI APIs are allowed for v1, but the backend venv does not currently include the OpenAI SDK. [VERIFIED: AGENTS.md; command `backend/.venv/bin/python -c "import openai"`]
   - What's unclear: Current OpenAI model/API choice and SDK methods were not checked because network was prohibited. [VERIFIED: user prompt]
   - Recommendation: Add a future implementation check against current official OpenAI docs before selecting transcription and structured-output code. [ASSUMED]

4. **How much source-clue scoring belongs in Phase 2?**
   - What we know: Phase 2 must support source-clue and claim-adjacent screenshots. [VERIFIED: 02-CONTEXT.md]
   - What's unclear: Whether deterministic OCR/regex is enough or whether vision model classification should be included. [ASSUMED]
   - Recommendation: Plan a deterministic baseline with fixture screenshots and keep a provider hook for later vision scoring. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Backend | yes | 3.12.1 | None needed. [VERIFIED: command `python3 --version`] |
| uv | Backend dependency management | yes | 0.5.26 | Existing backend venv can run tests. [VERIFIED: command `uv --version`] |
| pytest | Backend tests | yes | 9.0.3 | None needed. [VERIFIED: command `backend/.venv/bin/pytest --version`] |
| Node | Frontend | yes | 22.18.0 | None needed. [VERIFIED: command `node --version`] |
| Yarn | Frontend | yes | 3.5.0 | None needed. [VERIFIED: command `yarn --version`] |
| Vitest | Frontend tests | yes | 4.1.4 | None needed. [VERIFIED: command `frontend/node_modules/.bin/vitest --version`] |
| Docker | MongoDB/Qdrant local services | yes | 28.5.1 | Host-only tests can use mocks. [VERIFIED: command `docker --version`] |
| Docker Compose | MongoDB/Qdrant local services | yes | v2.40.2-desktop.1 | Host-only tests can use mocks. [VERIFIED: command `docker compose version`] |
| MongoDB service | Local metadata store | compose-defined | mongodb-community-server latest | Unit tests should mock repositories; integration tests can use Compose. [VERIFIED: infra/docker-compose.yml] |
| Qdrant service | Vector target | compose-defined | latest image | Phase 2 can avoid vector indexing or use contract-only payload tests. [VERIFIED: infra/docker-compose.yml; .planning/ROADMAP.md] |
| yt-dlp CLI | TikTok adapter | yes | 2026.02.04 | Fixture/pasted transcript path. [VERIFIED: command `yt-dlp --version`; 02-CONTEXT.md] |
| ffmpeg | Transcription prep | yes | 8.0.1 | Skip transcription fallback when media gate is closed. [VERIFIED: command `ffmpeg -version`; 02-CONTEXT.md] |
| OpenCV Python in backend venv | Keyframes | no | - | Add `opencv-python` or skip live keyframes in tests using fixtures. [VERIFIED: command `backend/.venv/bin/python -c "import cv2"`] |
| OpenAI SDK in backend venv | Transcription and claim extraction | no | - | Add dependency; tests should mock provider. [VERIFIED: command `backend/.venv/bin/python -c "import openai"`] |
| Pillow in backend venv | OCR/image preprocessing | no | - | Only add if OCR path is selected. [VERIFIED: command `backend/.venv/bin/python -c "import PIL"`] |
| Tesseract CLI | Optional OCR | yes | 5.5.1 | Use transcript-only and fixture visual text if OCR is deferred. [VERIFIED: command `tesseract --version`] |

**Missing dependencies with no fallback:**

- None for planning, because the fixture/pasted-transcript path can validate job, transcript, claim extraction, triage, and UI behavior without live TikTok access. [VERIFIED: 02-CONTEXT.md]

**Missing dependencies with fallback:**

- `openai` SDK: mock in tests and add before live transcription/LLM extraction. [VERIFIED: command `backend/.venv/bin/python -c "import openai"`]
- `opencv-python`: use fixture keyframe artifacts in tests until installed. [VERIFIED: command `backend/.venv/bin/python -c "import cv2"`]
- `Pillow`/`pytesseract`: defer OCR or use transcript-only source-candidate triage. [VERIFIED: command `backend/.venv/bin/python -c "import PIL"`; command `backend/.venv/bin/python -c "import pytesseract"`]

## Phase Validation and Test Strategy

`workflow.nyquist_validation` is explicitly `false`, so the formal GSD `Validation Architecture` section is skipped; this section records practical test strategy because the user requested it. [VERIFIED: .planning/config.json; user prompt]

### Backend Tests

| Test Area | What to Cover | Suggested Command |
|-----------|---------------|-------------------|
| URL validation and unsupported URL recovery | Only public TikTok URL formats accepted; unsupported URL creates failed/recoverable state. [VERIFIED: .planning/REQUIREMENTS.md; 02-UI-SPEC.md] | `cd backend && uv run pytest tests/test_ingestion_api.py -x` |
| Compliance gate | Media download skipped when gate is closed; progress records skipped/compliance reason. [VERIFIED: AGENTS.md; 02-CONTEXT.md] | `cd backend && uv run pytest tests/test_compliance.py -x` |
| Transcript provenance | Captions, subtitle, transcription, pasted, and fixture methods are distinguishable. [VERIFIED: 02-CONTEXT.md] | `cd backend && uv run pytest tests/test_transcript.py -x` |
| Keyframe artifacts | Frame records have UUIDs, timestamps, vault paths, and source-clue flags. [VERIFIED: 02-CONTEXT.md] | `cd backend && uv run pytest tests/test_keyframes.py -x` |
| Claim extraction parsing | Valid LLM JSON produces atomic claims; parse failure does not fabricate claims. [VERIFIED: 02-UI-SPEC.md] | `cd backend && uv run pytest tests/test_claim_extraction.py -x` |
| Research-basis triage | DOI/arXiv/URL/paper-like clues produce candidates; no clues produces opinion/unratable or no-source status. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md] | `cd backend && uv run pytest tests/test_research_basis.py -x` |
| Vault/Mongo persistence | Entity UUIDs, slugs, frontmatter, and relationships are written without duplicate canonical entities. [VERIFIED: docs/phase-1-contracts.md; backend/app/repositories/mongo.py] | `cd backend && uv run pytest tests/test_ingestion_persistence.py -x` |

### Frontend Tests

| Test Area | What to Cover | Suggested Command |
|-----------|---------------|-------------------|
| Submission flow | URL form submits, disables duplicate submit, reserves job UUID space, and shows recoverable errors. [VERIFIED: 02-UI-SPEC.md] | `cd frontend && yarn test --run` |
| Progress timeline | Steps render pending/running/complete/failed/skipped and `aria-live="polite"` updates. [VERIFIED: 02-UI-SPEC.md] | `cd frontend && yarn test --run` |
| Artifact panels | Metadata, transcript, media, screenshots, claims, and triage statuses render from normalized DTOs. [VERIFIED: 02-UI-SPEC.md] | `cd frontend && yarn test --run` |
| Claim selection | Selecting a claim highlights transcript excerpt and related screenshots. [VERIFIED: 02-UI-SPEC.md] | `cd frontend && yarn test --run` |
| Responsive layout | Mobile keeps main pane before right-rail metadata and uses 44px touch targets. [VERIFIED: 02-UI-SPEC.md] | `cd frontend && yarn build` plus targeted component tests |

### Fixture Strategy

- Add a pasted-transcript fixture with two timestamped AI research claims and one DOI/arXiv/source clue. [VERIFIED: 02-CONTEXT.md]
- Add a no-source fixture that produces `opinion_or_unratable` or `no_research_source_found`. [VERIFIED: 02-CONTEXT.md; 02-UI-SPEC.md]
- Add a parse-failure fixture that keeps transcript visible and marks claim extraction failed. [VERIFIED: 02-UI-SPEC.md]
- Add source-clue screenshot fixture metadata without requiring live TikTok download. [VERIFIED: 02-CONTEXT.md]
- Mock `yt-dlp`, OpenAI, OpenCV, and OCR in unit tests so tests do not depend on network or platform availability. [VERIFIED: user prompt]

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so this research treats security coverage as enabled. [VERIFIED: .planning/config.json]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Phase 2 has no login/auth scope. [VERIFIED: .planning/ROADMAP.md; frontend/src/components/AppShell.tsx] |
| V3 Session Management | no | Phase 2 has no sessions. [VERIFIED: .planning/ROADMAP.md] |
| V4 Access Control | limited | Enforce public TikTok-only input and no private/paywalled ingestion. [VERIFIED: .planning/REQUIREMENTS.md; AGENTS.md] |
| V5 Input Validation | yes | Validate TikTok URL, job UUIDs, Pydantic payloads, LLM output, and source-candidate fields. [VERIFIED: backend/app/schemas/entities.py; 02-CONTEXT.md] |
| V6 Cryptography | no new crypto | Store no API keys, provider tokens, passwords, or secret env values in Markdown/logs. [VERIFIED: docs/phase-1-contracts.md] |

### Known Threat Patterns for Phase 2

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Prompt injection in captions/transcripts/OCR | Tampering | Wrap external text with `wrap_untrusted_text()` and validate schema output. [VERIFIED: backend/app/safety/input_boundaries.py] |
| XSS from public-page metadata/transcript/visual text | Tampering | Render as plain text only; never render untrusted external HTML. [VERIFIED: 02-UI-SPEC.md] |
| SSRF or arbitrary URL download | Tampering / Information Disclosure | Accept only public TikTok URL formats and keep media retrieval behind adapter and compliance gate. [VERIFIED: AGENTS.md; 02-CONTEXT.md] |
| Secret leakage into vault/logs | Information Disclosure | Keep provider credentials in environment/config and never write them to Markdown or logs. [VERIFIED: docs/phase-1-contracts.md] |
| Duplicate or corrupted canonical records on rerun | Tampering | Upsert by UUID and external aliases; keep job UUID separate from entity UUIDs. [VERIFIED: docs/phase-1-contracts.md; backend/app/repositories/mongo.py] |
| Overstated truth claims | Repudiation | Do not show Phase 4 evidence labels or verification copy in Phase 2. [VERIFIED: 02-UI-SPEC.md; .planning/ROADMAP.md] |

## Future Implementation Checks

These checks were intentionally not performed because the user requested no network dependency. [VERIFIED: user prompt]

- Check current official OpenAI docs for transcription API, structured outputs, JSON schema behavior, model selection, timeout/retry patterns, and SDK version before implementing live provider calls. [ASSUMED]
- Check current `yt-dlp` docs and release notes before relying on TikTok extractor behavior, subtitle flags, output templates, and download limits. [ASSUMED]
- Check a current caption parser package and docs before selecting `webvtt-py`, `srt`, or a narrow internal parser. [ASSUMED]
- Check OpenCV/Pillow/Tesseract install behavior on the target deployment environment before requiring OCR in the default path. [ASSUMED]
- Check FastAPI docs for the selected background-task or streaming/polling pattern if the planner chooses SSE or long-running in-process workers. [ASSUMED]

## Sources

### Primary (HIGH confidence)

- `AGENTS.md` - project constraints, v1 scope, storage ownership, compliance gate, allowed OpenAI usage.
- `.planning/PROJECT.md` - product vision, active requirements, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` - Phase 2 requirement IDs and boundaries.
- `.planning/ROADMAP.md` - Phase 2 goal, success criteria, and later-phase boundaries.
- `.planning/STATE.md` - Phase status and sequencing.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-CONTEXT.md` - locked Phase 2 decisions.
- `.planning/phases/02-tiktok-ingestion-and-claim-extraction/02-UI-SPEC.md` - approved UI design and interaction contract.
- `.planning/phases/01-foundation-and-knowledge-store-contracts/01-CONTEXT.md` - Phase 1 locked stack/store/UUID decisions.
- `docs/phase-1-contracts.md` and `vault/SCHEMA.md` - UUID, vault, MongoDB, Qdrant, operations, safety contracts.
- `backend/app/contracts/logging.py`, `backend/app/safety/input_boundaries.py`, `backend/app/schemas/entities.py`, `backend/app/schemas/relationships.py`, `backend/app/contracts/vault.py`, `backend/app/repositories/mongo.py` - current backend contracts and patterns.
- `frontend/src/components/AppShell.tsx`, `frontend/src/styles/app.css`, `frontend/src/styles/tokens.css` - current frontend shell and styling constraints.
- `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent/src/extraction/video.py` - local `yt-dlp` and OpenCV extraction reference.
- `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent/src/extraction/queue.py` - local progress, duplicate/permanent failure, transcript reference, and video processing reference.

### Secondary (MEDIUM confidence)

- Local command probes for tool availability: `python3 --version`, `node --version`, `yarn --version`, `uv --version`, `yt-dlp --version`, `ffmpeg -version`, `tesseract --version`, Docker versions, backend venv import checks.
- Lockfiles: `backend/uv.lock`, `frontend/yarn.lock`.

### Tertiary (LOW confidence)

- Assumptions in the Assumptions Log and Future Implementation Checks. These need confirmation before implementation locks model/provider/parser choices.

## Metadata

**Confidence breakdown:**

- Standard stack: MEDIUM - local versions and missing dependencies are verified, but new package versions and external API details were not checked because network access was prohibited. [VERIFIED: user prompt; backend/uv.lock; frontend/yarn.lock]
- Architecture: HIGH - architecture follows locked Phase 1/2 decisions and current code boundaries. [VERIFIED: 01-CONTEXT.md; 02-CONTEXT.md; docs/phase-1-contracts.md]
- Pitfalls: HIGH for local pitfalls - timestamp loss, scope creep, and vault contract gaps are verified in local code/artifacts. [VERIFIED: stoz3n-chat-agent/src/extraction/video.py; stoz3n-chat-agent/src/extraction/queue.py; backend/app/contracts/vault.py]
- External implementation details: LOW - OpenAI, current `yt-dlp` TikTok behavior, caption parser choice, and OCR stack need official-doc/version checks during implementation. [VERIFIED: user prompt]

**Research date:** 2026-04-18
**Valid until:** 2026-04-25 for external platform/provider details; local architecture constraints remain valid until Phase 2 decisions change. [ASSUMED]
