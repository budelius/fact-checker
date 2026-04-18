# Phase 2 Ingestion

## Scope

Phase 2 accepts public TikTok URLs, pasted transcript fixtures, and user-owned video uploads. It creates ingestion jobs, exposes progress, stores uploaded video media locally, builds transcript artifacts when text is available, extracts local fixture claims, and triages whether source candidates are present.

Phase 2 stops at video-derived context and source-candidate triage. It does not perform paper discovery, paper downloading, evidence evaluation, ratings, vector indexing, or graph browsing.

## API Routes

- `POST /ingestion/tiktok` accepts a public TikTok URL and creates a pending job.
- `POST /ingestion/videos/upload` accepts a multipart video file and optional transcript text.
- `POST /ingestion/fixtures/transcript` accepts a source URL and pasted transcript text for local development and tests.
- `GET /ingestion/jobs/{job_uuid}` returns the stored job payload or `ingestion_job_not_found`.

## Progress Stages

Jobs expose ordered stage records using these names:

- `validate_url`
- `read_public_metadata`
- `build_transcript`
- `capture_source_clues`
- `extract_claims`
- `triage_research_basis`
- `write_owned_artifacts`

Each stage uses `pending`, `running`, `succeeded`, `failed`, or `skipped`. The frontend displays `succeeded` as complete while keeping the backend value intact.

## Artifact Types

Phase 2 artifacts include public metadata, transcript, media retrieval, screenshots/keyframes, claims, and research basis. Extracted claims keep `evidence_status` as `pending`; Phase 4 owns supported, contradicted, mixed, and insufficient-evidence labels.

## Compliance Gate

`TIKTOK_MEDIA_DOWNLOAD_ENABLED=false` is the default. Live TikTok media download and transcription fallback must stay behind this explicit setting. Local fixture tests do not call TikTok, OpenAI, yt-dlp, OpenCV, or paper search.

## Video Upload Path

Uploaded files are stored locally under `vault/raw/videos/` and returned as media-retrieval artifacts. The upload route records `third_party_upload=false`; uploaded videos are not sent to third-party providers by default. If an upload does not include transcript text and no transcription provider is enabled, transcript and claim extraction are skipped with recoverable status messages.

## Fixture And Pasted Transcript Path

`POST /ingestion/fixtures/transcript` runs a local, deterministic path for development and tests. It builds a transcript artifact, extracts local fixture claims with `evidence_status: pending`, triages source candidates such as arXiv IDs or DOIs, and stores the resulting job payload for polling.

## Research-Basis Triage

Research-basis triage records source candidates only. Candidate values can include DOI, arXiv, URL, paper title, named study, author, or article title. Candidate presence means "ready for paper discovery"; it does not mean a paper has been found, downloaded, evaluated, or rated.

## Out Of Scope

- Full paper discovery and paper download.
- Paper parsing, chunking, summaries, and indexing.
- Evidence comparison and fact-check labels.
- Creator, author, paper, or source ratings.
- Knowledge graph browsing and vector search UI.

## Verification Commands

```bash
cd backend && uv run pytest -q
cd frontend && yarn build
```
