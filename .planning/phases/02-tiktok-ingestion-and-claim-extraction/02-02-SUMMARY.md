---
phase: 02-tiktok-ingestion-and-claim-extraction
plan: "02"
subsystem: backend
tags: [fastapi, ingestion, tiktok, yt-dlp, transcript, keyframes]
requires:
  - phase: 02-tiktok-ingestion-and-claim-extraction
    provides: Plan 01 ingestion schemas and vault artifact contracts
provides:
  - Default-deny media download compliance settings
  - TikTok URL validation and mocked yt-dlp metadata/subtitle adapter
  - Timestamp-preserving transcript normalization
  - Source-clue screenshot artifact helpers with OpenCV fallback
affects: [phase-2-api, phase-2-claims, phase-2-ui]
tech-stack:
  added: []
  patterns: [default-deny media compliance, adapter boundary, timestamped transcript parsing]
key-files:
  created:
    - backend/app/ingestion/compliance.py
    - backend/app/ingestion/adapters/tiktok.py
    - backend/app/ingestion/transcript.py
    - backend/app/ingestion/keyframes.py
  modified:
    - backend/app/settings.py
    - .env.example
key-decisions:
  - "Media download remains disabled unless TIKTOK_MEDIA_DOWNLOAD_ENABLED explicitly enables it."
  - "TikTok-specific subprocess behavior is isolated behind backend/app/ingestion/adapters/tiktok.py."
  - "OpenCV is imported inside the keyframe function so tests and dev environments can run without it."
patterns-established:
  - "Adapters validate URL support before any subprocess or platform call."
  - "Transcript parsing preserves cue timing when VTT/SRT timing is available."
requirements-completed: [ING-03, ING-04, ING-05, CLM-02]
duration: 12min
completed: 2026-04-18
---

# Phase 2 Plan 02 Summary

**Default-deny TikTok media adapter with timestamped transcript parsing and source-clue screenshot scaffolding**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-18T11:57:00Z
- **Completed:** 2026-04-18T12:08:58Z
- **Tasks:** 4
- **Files modified:** 12

## Accomplishments

- Added media compliance settings and `.env.example` defaults for disabled media download/transcription.
- Added TikTok URL validation plus async `yt-dlp` metadata/subtitle helpers covered by mocked subprocess tests.
- Added VTT/SRT timestamp parsing and plain-text transcript artifact helpers.
- Added source-clue detection for DOI, arXiv, URLs, and paper-like phrases with safe OpenCV fallback.

## Task Commits

1. **Task 1: Add compliance settings and default-deny policy** - included in plan commit.
2. **Task 2: Add TikTok adapter with mocked yt-dlp metadata and subtitle paths** - included in plan commit.
3. **Task 3: Add timestamp-preserving transcript normalization** - included in plan commit.
4. **Task 4: Add keyframe artifact helper with safe OpenCV fallback** - included in plan commit.

## Files Created/Modified

- `backend/app/ingestion/compliance.py` - Media compliance decision model and default-deny helper.
- `backend/app/ingestion/adapters/tiktok.py` - TikTok URL validator plus metadata/subtitle subprocess boundary.
- `backend/app/ingestion/transcript.py` - Timestamp parsing and transcript artifact construction.
- `backend/app/ingestion/keyframes.py` - Source-clue scoring and screenshot artifact helpers.
- `backend/tests/test_compliance.py` - Compliance defaults and enabled-path tests.
- `backend/tests/test_tiktok_adapter.py` - Adapter URL/subprocess behavior tests.
- `backend/tests/test_transcript.py` - VTT/SRT/plain-text transcript parsing tests.
- `backend/tests/test_keyframes.py` - Source clue and OpenCV fallback tests.
- `backend/app/settings.py` and `.env.example` - Phase 2 ingestion settings.

## Decisions Made

- Rejected unsupported URLs with `unsupported_tiktok_url` before subprocess creation.
- Returned empty metadata/subtitle results on subprocess failure instead of raising, so job orchestration can show recoverable states.
- Kept keyframe extraction artifact-only for now; actual file writes belong to orchestration/persistence.

## Deviations from Plan

None - plan executed exactly as written.

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope creep.

## Issues Encountered

None.

## Verification

- `cd backend && uv run pytest tests/test_compliance.py tests/test_tiktok_adapter.py tests/test_transcript.py tests/test_keyframes.py -q` -> 12 passed.
- `grep -q "TIKTOK_MEDIA_DOWNLOAD_ENABLED=false" .env.example` -> passed.
- `grep -q "def is_supported_tiktok_url" backend/app/ingestion/adapters/tiktok.py` -> passed.
- `grep -q "def parse_vtt_segments" backend/app/ingestion/transcript.py` -> passed.
- `grep -q "def score_source_clue_text" backend/app/ingestion/keyframes.py` -> passed.

## User Setup Required

None - media download and transcription remain disabled by default.

## Next Phase Readiness

Claim extraction and research-basis triage can consume normalized `TranscriptArtifact` data and source-clue text without knowing TikTok-specific adapter behavior.

---
*Phase: 02-tiktok-ingestion-and-claim-extraction*
*Completed: 2026-04-18*
