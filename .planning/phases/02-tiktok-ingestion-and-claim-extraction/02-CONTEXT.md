# Phase 2: TikTok Ingestion and Claim Extraction - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 lets a user submit a public TikTok URL from the web app, creates a visible job with useful progress, retrieves public metadata/transcript/media context through an ingestion adapter, captures representative screenshots/keyframes, and extracts timestamped atomic AI research claims. It also performs an early research-basis triage by extracting paper-like or source-like references from transcript and visual context.

This phase does not perform full paper discovery, paper downloading, evidence evaluation, creator ratings, author ratings, or graph browsing. Those belong to later phases. If Phase 2 cannot find research/source candidates in the video content, it should mark the video or claims as opinion-based/unratable for now rather than pretending evidence exists.

</domain>

<decisions>
## Implementation Decisions

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

### the agent's Discretion

- Exact backend route names, service module names, and MongoDB collection names, as long as they follow Phase 1 UUID and repository/module boundaries.
- Exact progress transport for v1, such as polling, server-sent events, or a simple refresh loop, as long as the user can see meaningful stage updates.
- Exact screenshot/keyframe selection algorithm, as long as it prioritizes source clues and claim context.
- Exact field names for research-basis status, as long as the states distinguish source candidates found, no research source found, opinion/unratable, and needs manual review.
- Exact LLM prompt wording and JSON schema details, as long as untrusted-input handling and parse-failure behavior are explicit.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project and Phase Requirements

- `.planning/PROJECT.md` - Product vision, ownership goals, and why the system should build a reusable knowledge base rather than rely only on ChatGPT.
- `.planning/ROADMAP.md` - Phase 2 goal, success criteria, implementation notes, and later-phase boundaries.
- `.planning/REQUIREMENTS.md` - Requirements `ING-01` to `ING-05`, `CLM-01` to `CLM-03`, and `UI-01`.
- `.planning/STATE.md` - Current project status and phase sequencing.
- `.planning/phases/01-foundation-and-knowledge-store-contracts/01-CONTEXT.md` - Locked Phase 1 decisions for monorepo, MongoDB, Qdrant, Markdown vault, UUIDs, and provider boundaries.
- `docs/phase-1-contracts.md` - UUID, Markdown, MongoDB/Qdrant, untrusted-source, and out-of-scope contracts from Phase 1.

### Existing Contracts and Code

- `backend/app/contracts/logging.py` - Pipeline logging event/status contract for job-stage progress.
- `backend/app/safety/input_boundaries.py` - Required boundary for untrusted transcript/video/web content before LLM use.
- `backend/app/schemas/entities.py` - Existing UUID/entity schema patterns.
- `backend/app/schemas/relationships.py` - Existing relationship schema pattern for graph-like links in MongoDB.
- `backend/app/contracts/vault.py` - Markdown/frontmatter path and slug conventions.
- `vault/SCHEMA.md` - Human-readable vault structure and entity note expectations.
- `frontend/src/components/AppShell.tsx` - Current React shell where the submission/progress UI must fit.
- `frontend/src/styles/app.css` and `frontend/src/styles/tokens.css` - Existing frontend visual language and layout constraints.

### User-Referenced Local Implementation

- `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent/src/extraction/video.py` - Reference implementation for `yt-dlp` metadata extraction, subtitle extraction, video download, and OpenCV keyframe extraction.
- `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent/src/extraction/queue.py` - Reference implementation for reporting video-processing progress, extracting transcript references, and discovering source candidates. Use as inspiration only; do not copy architecture blindly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `backend/app/contracts/logging.py`: Use the existing pipeline logging contract to record job progress and expose current operation to the UI.
- `backend/app/safety/input_boundaries.py`: Wrap transcript, OCR, captions, visual text, and public-page metadata as untrusted external content before sending to an LLM.
- `backend/app/contracts/vault.py` and `vault/SCHEMA.md`: Use existing vault conventions for video, transcript, screenshot/keyframe, and claim Markdown artifacts.
- `frontend/src/components/AppShell.tsx`: Extend the existing knowledge workbench shell rather than creating a landing page.

### Established Patterns

- The repo is a monorepo with `backend/`, `frontend/`, `infra/`, and `vault/`.
- Backend code is Python/FastAPI with Pydantic schemas and repository/service boundaries.
- MongoDB is the primary structured metadata and graph relationship store; Qdrant is not the source of truth.
- UUIDs are canonical IDs. TikTok IDs, URLs, usernames, and transcript provider IDs are aliases or metadata.
- Markdown is the owned, human-readable knowledge layer.

### Integration Points

- Backend should add ingestion/job APIs that the React UI can call.
- Ingestion adapter should normalize TikTok-specific results into video, transcript, screenshot/keyframe, and claim artifacts.
- Claim extraction should consume normalized transcript/visual context, not raw TikTok adapter details.
- Job progress should be persisted in MongoDB and also represented in logs using the Phase 1 logging contract.
- Vault writes should produce human-readable notes and raw asset references without storing secrets or unsafe rendered external HTML.

</code_context>

<specifics>
## Specific Ideas

- The progress UI should show what the agent is actually doing at each stage.
- Transcript retrieval should first try the public video page/captions, then try video download plus transcription if captions are unavailable.
- The prior `stoz3n-chat-agent` project is a useful implementation reference for transcript and video-frame handling.
- Screenshots should help the user remember the video and should preferentially capture visible paper/source clues.
- If no paper/source references are found, the system should say the content appears opinion-based or cannot be rated for now.
- A valuable early outcome is simply identifying whether a video is research-based at all.

</specifics>

<deferred>
## Deferred Ideas

- Full paper discovery, paper downloading, paper indexing, and Markdown paper summaries - Phase 3.
- Comparing claims against papers and judging truthfulness - Phase 4.
- Creator ratings, author ratings, source ratings, knowledge graph browsing, and vector search UI - Phase 5.
- Real-time smart-glasses or meeting-assistant fact checking - future milestone, not v1 Phase 2.

</deferred>

---

*Phase: 02-tiktok-ingestion-and-claim-extraction*
*Context gathered: 2026-04-18*
