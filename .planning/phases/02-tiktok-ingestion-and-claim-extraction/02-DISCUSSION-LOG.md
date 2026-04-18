# Phase 2: TikTok Ingestion and Claim Extraction - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 02-TikTok Ingestion and Claim Extraction
**Areas discussed:** Submission and progress UX, TikTok adapter, transcript fallback and provenance, visual context capture, claim extraction and research-basis triage

---

## Submission and Progress UX

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal status | Show only pending/running/failed/complete. | |
| Stage progress | Show lifecycle status plus what the backend is doing now. | yes |
| Detailed logs | Expose full pipeline logs in the UI. | |

**User's choice:** Show some progress and what the agent is actually doing.
**Notes:** The UI should be useful while the backend works through transcript retrieval, media handling, screenshots, and claim extraction.

---

## TikTok Adapter

| Option | Description | Selected |
|--------|-------------|----------|
| Public transcript first | Retrieve transcript/captions from the public video page when available. | yes |
| Download fallback | Download public video and transcribe when transcript/captions are unavailable. | yes |
| Fixture only | Do not attempt live media retrieval in v1. | |

**User's choice:** Get the transcript from the public page of the video when possible; otherwise try to download the video and transcribe it.
**Notes:** User referenced `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent` as an existing implementation reference. The repo contains `src/extraction/video.py` with `yt-dlp` metadata/subtitle/video download and OpenCV frame extraction patterns.

---

## Transcript Fallback and Provenance

| Option | Description | Selected |
|--------|-------------|----------|
| Captions only | Stop when public captions are unavailable. | |
| Captions plus transcription | Use public page/captions first, then transcribe downloaded video when allowed. | yes |
| Pasted transcript only | Avoid live extraction and use manual transcript input. | |

**User's choice:** Same as adapter choice: public page transcript first, video download/transcription fallback.
**Notes:** The context captures explicit provenance requirements so later phases can distinguish captions, transcription, fixtures, and pasted transcripts.

---

## Visual Context Capture

| Option | Description | Selected |
|--------|-------------|----------|
| Creator context | Capture frames that show the creator/background. | |
| Source-clue frames | Capture frames likely to contain papers, links, slides, DOI/arXiv IDs, or article screenshots. | yes |
| No screenshots | Transcript-only ingestion. | |

**User's choice:** Ideally find something which looks like a paper in the background or links. The creator in the background is not necessary, but a few screenshots help to remember.
**Notes:** Exact frame count and heuristic are left to planning.

---

## Claim Extraction and Research-Basis Triage

| Option | Description | Selected |
|--------|-------------|----------|
| Extract claims only | Do not decide whether claims appear research-backed. | |
| Research-basis triage | Extract claims and source candidates, and mark content unratable/opinion-based if no sources are found. | yes |
| Full truth rating | Judge truthfulness in Phase 2. | |

**User's choice:** If nothing can be found in papers, say it is opinion-based and cannot be rated for now.
**Notes:** The important near-term value is quickly checking whether the content is research based at all. Full evidence search and truth evaluation remain later phases.

---

## the agent's Discretion

- Exact progress transport and stage enum details.
- Exact screenshot/keyframe count and selection algorithm.
- Exact schema field names for research-basis status and transcript provenance.

## Deferred Ideas

- Full paper discovery and paper processing remain Phase 3.
- Truthfulness evaluation remains Phase 4.
- Ratings and graph UI remain Phase 5.
