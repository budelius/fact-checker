# Fact Checker

Fact Checker is a user-owned AI research fact-checking system. A user pastes a public TikTok link, the backend retrieves public metadata, captions, and visual context, extracts timestamped claims, finds paper/preprint candidates, and stores durable knowledge in an owned Markdown vault with MongoDB and Qdrant indexes.

The original product thinking lives in [ideation.md](ideation.md). Read it first if you want the motivation, scope, and long-term direction behind the implementation.

## Current Scope

- Phase 1: app skeleton, vault contracts, MongoDB/Qdrant boundaries, and static knowledge-browser shell.
- Phase 2: public TikTok ingestion, captions, ffmpeg-backed source-clue frame extraction when enabled, claim extraction, and source-candidate triage.
- Phase 3: ground-truth discovery and paper processing is in progress: OpenAI web search, paper index clients, paper parsing/summarization/indexing, and owned artifacts.

Phase 4 evidence labels and final fact-check reports are not complete yet. Phase 2 claim rows intentionally show `evidence_status: pending`.

## Repository Layout

- `backend/` - FastAPI API, ingestion pipeline, ground-truth pipeline, schemas, tests.
- `frontend/` - React, TypeScript, Vite UI.
- `infra/` - local Docker Compose datastores.
- `vault/` - Obsidian-compatible Markdown knowledge base and raw artifact folders.
- `docs/` - phase and contract documentation.
- `.planning/` - GSD planning artifacts.

## Prerequisites

For the Docker Compose path, install:

- Docker and Docker Compose

For host-based development, also install:

- Python 3.12
- `uv`
- Node.js and Yarn
- `yt-dlp` for public TikTok metadata, captions, thumbnails, and optional video download
- `ffmpeg` for source-clue frame extraction when `TIKTOK_MEDIA_DOWNLOAD_ENABLED=true`

Example macOS setup:

```bash
brew install ffmpeg
brew install yt-dlp
curl -LsSf https://astral.sh/uv/install.sh | sh
corepack enable
```

## Environment

Create a local `.env` from the example:

```bash
cp .env.example .env
```

Put real secrets only in `.env`. Do not commit `.env`; it is git-ignored.

For the first version with OpenAI, set:

```bash
OPENAI_API_KEY=sk-proj-your-key-here

# Optional model overrides. These defaults are used when omitted.
OPENAI_DISCOVERY_MODEL=gpt-5.4-mini
OPENAI_SUMMARY_MODEL=gpt-5.4-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
# OPENAI_EMBEDDING_DIMENSIONS can be added only when you intentionally need it.
```

Optional paper-index settings:

```bash
OPENALEX_EMAIL=you@example.com
SEMANTIC_SCHOLAR_API_KEY=
GROUND_TRUTH_MAX_RESULTS_PER_PROVIDER=10
PAPER_DOWNLOAD_ENABLED=true
PAPER_MAX_PDF_MB=40
PAPER_REQUEST_TIMEOUT_SECONDS=20
```

TikTok media settings:

```bash
TIKTOK_MEDIA_DOWNLOAD_ENABLED=false
TIKTOK_MAX_VIDEO_MB=200
TRANSCRIPTION_PROVIDER=disabled
```

`TIKTOK_MEDIA_DOWNLOAD_ENABLED=false` keeps live video download disabled. Captions and public metadata can still work through `yt-dlp`. Set it to `true` only when you want the backend to download public video bytes and extract a real source-clue frame with ffmpeg.

## Run With Docker Compose

Docker Compose can run the application stack plus datastores. You only need Docker installed and a local `.env` for secrets such as `OPENAI_API_KEY`.

```bash
cd infra
docker compose --env-file ../.env up -d --build
docker compose ps
```

Open the frontend:

```text
http://127.0.0.1:5173/
```

The backend is exposed at:

```text
http://127.0.0.1:8000/
```

MongoDB is intentionally not published to the Mac host by the default compose file, so it does not conflict with a local MongoDB on `27017`. The backend connects to MongoDB over the Compose network using the `mongodb` service name. Qdrant is published on `6333` and `6334`.

The backend Docker image installs `ffmpeg` and `yt-dlp`, so TikTok caption retrieval and gated frame extraction work inside the container. `TIKTOK_MEDIA_DOWNLOAD_ENABLED=false` still remains the default.

Stop the stack:

```bash
cd infra
docker compose down
```

Delete local datastore volumes:

```bash
cd infra
docker compose down -v
```

This deletes local MongoDB and Qdrant data.

## Run Host Development

Use this path when editing code directly on the host.

If you run the backend on the host and need MongoDB-backed Phase 3 persistence, `MONGODB_URI` must point to a MongoDB instance reachable from the host. If you use your local Mac MongoDB, set `MONGODB_URI` accordingly in `.env`. If you want the backend to use the Compose MongoDB, run the backend in the Docker network or explicitly publish MongoDB on a non-conflicting host port.

Start only the datastores:

```bash
cd infra
docker compose --env-file ../.env up -d mongodb qdrant
docker compose ps
```

Install dependencies:

Backend:

```bash
cd backend
uv sync
```

Frontend:

```bash
cd frontend
yarn install
```

Start the backend:

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
yarn dev --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173/
```

The frontend calls the backend at `http://127.0.0.1:8000` by default. Override with `VITE_API_BASE_URL` when needed:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 yarn dev --host 127.0.0.1 --port 5173
```

## First Run

1. Start datastores with Docker Compose.
2. Start the backend.
3. Start the frontend.
4. Paste a public TikTok URL into the UI.
5. Click `Check video`.

For a known local test example:

```text
https://www.tiktok.com/@stephenlee96/video/7626043894639250702?_r=1&_t=ZN-95VcdJG75OA
```

Expected Phase 2 behavior:

- public metadata is retrieved
- captions are loaded when available
- claims are extracted with `evidence_status: pending`
- source candidates are prepared for paper discovery
- screenshot/keyframe preview is shown when a source-clue image is available

## API Smoke Tests

Backend health:

```bash
curl http://127.0.0.1:8000/health
```

Submit TikTok ingestion:

```bash
curl -X POST http://127.0.0.1:8000/ingestion/tiktok \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.tiktok.com/@stephenlee96/video/7626043894639250702?_r=1&_t=ZN-95VcdJG75OA"}'
```

Start ground-truth discovery from an ingestion job:

```bash
curl -X POST http://127.0.0.1:8000/ground-truth/jobs/from-ingestion/{ingestion_job_uuid}
```

Fetch a ground-truth job:

```bash
curl http://127.0.0.1:8000/ground-truth/jobs/{ground_truth_job_uuid}
```

## Verification

Backend tests and lint:

```bash
cd backend
uv run pytest -q
uv run ruff check app tests
```

Frontend build:

```bash
cd frontend
yarn build
```

## Knowledge Ownership

Markdown remains the canonical human-readable knowledge surface. Raw artifacts live under `vault/raw/`, generated notes live under `vault/wiki/`, MongoDB stores structured metadata and relationships, and Qdrant stores vector-search points. OpenAI can be used for v1 discovery, summarization, and embeddings, but durable knowledge should stay in the user-owned stores.

## Security Notes

- Never commit `.env`, API keys, provider tokens, downloaded private media, or private source material.
- Treat TikTok captions, transcripts, PDFs, OCR text, and web content as untrusted input.
- Keep `TIKTOK_MEDIA_DOWNLOAD_ENABLED=false` unless you explicitly want local video download and ffmpeg frame extraction for public videos.
- `.env.example` must contain placeholders only, never real credentials.
