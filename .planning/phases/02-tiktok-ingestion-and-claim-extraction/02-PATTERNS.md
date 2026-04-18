# Phase 2: TikTok Ingestion and Claim Extraction - Pattern Map

**Mapped:** 2026-04-18
**Status:** Ready for planning
**Source:** Local orchestrator fallback after pattern-mapper agent stalled during MCP startup

## Purpose

This file maps likely Phase 2 implementation files to existing analogs and contracts. It is a planner input only; it does not replace `02-RESEARCH.md`, `02-CONTEXT.md`, or `02-UI-SPEC.md`.

## Backend Patterns

### API Router

**Likely files**

- `backend/app/api/__init__.py`
- `backend/app/api/ingestion.py`
- `backend/app/main.py`

**Closest existing analog**

- `backend/app/main.py` currently defines direct FastAPI routes:

```python
app = FastAPI(title="Fact Checker API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "fact-checker-backend"}
```

**Planning guidance**

- Add an `APIRouter` for ingestion rather than growing `main.py` with many routes.
- Keep routes thin: validate request DTOs, call ingestion services, return normalized job DTOs.
- Required routes for Phase 2 planning:
  - `POST /ingestion/tiktok`
  - `POST /ingestion/fixtures/transcript` or equivalent pasted-transcript/dev path
  - `GET /ingestion/jobs/{job_uuid}`

### Schemas

**Likely files**

- `backend/app/schemas/ingestion.py`
- `backend/app/schemas/claims.py`
- `backend/app/schemas/entities.py`
- `backend/app/schemas/relationships.py`

**Closest existing analog**

- `backend/app/schemas/entities.py` uses Pydantic models, UUID identity, enums, and list defaults:

```python
class EntityType(str, Enum):
    video = "video"
    creator = "creator"
    transcript = "transcript"
    screenshot = "screenshot"
    claim = "claim"


class KnowledgeEntity(BaseModel):
    uuid: UUID
    entity_type: EntityType
    slug: str
    title: str
    vault_path: str
```

**Planning guidance**

- Follow Pydantic v2 `BaseModel` style.
- Use UUIDs for every job artifact and canonical entity.
- Keep job UUID separate from video/transcript/screenshot/claim UUIDs.
- Add explicit enums for lifecycle, stage status, transcript method, artifact type, research-basis status, and `evidence_status = "pending"`.

### Progress Logging

**Likely files**

- `backend/app/ingestion/progress.py`
- `backend/app/ingestion/jobs.py`
- `backend/app/contracts/logging.py`

**Closest existing analog**

- `backend/app/contracts/logging.py` provides the status vocabulary and required event shape:

```python
PIPELINE_EVENT_STATUSES = ("pending", "running", "succeeded", "failed", "skipped")


def build_pipeline_log_event(
    event_type: str,
    job_uuid: str,
    stage: str,
    status: str,
    message: str,
    created_at: str,
    entity_uuid: str | None = None,
) -> dict[str, str | None]:
```

**Planning guidance**

- Reuse `build_pipeline_log_event()` for stage events.
- Store a normalized job document in MongoDB with:
  - lifecycle status
  - current operation
  - ordered stage records
  - artifact status records
  - recoverable error details
- UI may display `succeeded` as `complete`, but backend should preserve raw status.

### MongoDB Repository

**Likely files**

- `backend/app/repositories/mongo.py`
- `backend/app/ingestion/jobs.py`
- `backend/app/ingestion/persistence.py`

**Closest existing analog**

- `MongoRepository` uses collection properties and UUID upserts:

```python
def upsert_entity(self, entity: KnowledgeEntity) -> None:
    document = entity.model_dump(mode="json")
    self.entities.update_one({"uuid": str(entity.uuid)}, {"$set": document}, upsert=True)
```

**Planning guidance**

- Add explicit collections for operational ingestion jobs and pipeline events, or add a dedicated `IngestionJobRepository`.
- Do not mix operational job status with canonical entity docs unless the plan specifies why.
- Upsert canonical entities by UUID; deduplicate video entities by external aliases only through deliberate service logic.

### Vault Contracts

**Likely files**

- `backend/app/contracts/vault.py`
- `vault/SCHEMA.md`
- `backend/app/ingestion/persistence.py`

**Closest existing analog**

- `expected_wiki_path()` returns slug-only paths:

```python
def expected_wiki_path(entity_type: str, slug: str) -> str:
    return f"vault/wiki/{entity_type}/{slug}.md"
```

**Planning guidance**

- Plan an early contract task for transcript and screenshot storage because `EntityType` includes `transcript` and `screenshot`, while `VAULT_WIKI_ENTITY_FOLDERS` omits transcript/screenshot folders.
- Keep raw external inputs under `vault/raw/`; generated notes under `vault/wiki/`.
- UUIDs belong in frontmatter, not filenames.

### Untrusted Input Boundary

**Likely files**

- `backend/app/ingestion/claims.py`
- `backend/app/ingestion/research_basis.py`
- `backend/app/safety/input_boundaries.py`

**Closest existing analog**

- `wrap_untrusted_text()` wraps external text:

```python
def wrap_untrusted_text(label: str, content: str) -> str:
    return (
        f"{UNTRUSTED_EXTERNAL_TEXT_WARNING}\n"
        f"Label: {label}\n"
        "<untrusted_content>\n"
        f"{content}\n"
        "</untrusted_content>"
    )
```

**Planning guidance**

- Every transcript, caption, OCR string, visual text, and public-page metadata block must be wrapped before LLM use.
- UI must render this content as plain text only.
- Parse failures must be explicit job/artifact states; do not fabricate claims.

### TikTok Adapter Reference

**Likely files**

- `backend/app/ingestion/compliance.py`
- `backend/app/ingestion/adapters/tiktok.py`
- `backend/app/ingestion/transcript.py`
- `backend/app/ingestion/keyframes.py`

**Closest local reference**

- `/Users/budelius/Documents/Projects/STOZ3N/stoz3n-chat-agent/src/extraction/video.py`

Useful patterns:

- `yt-dlp --dump-json --no-download` for metadata
- subtitle extraction with `--write-auto-subs`, `--write-subs`, `--sub-langs`, and `--convert-subs vtt`
- bounded video download with `--max-filesize`
- OpenCV `VideoCapture` and PNG frame encoding

Do not copy as-is:

- `_clean_vtt()` removes timestamps, which conflicts with CLM-02.
- direct video download must be behind the Phase 2 compliance gate.

## Frontend Patterns

### App Shell

**Likely files**

- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/ingestion/*`
- `frontend/src/api/ingestion.ts`

**Closest existing analog**

- `AppShell` is a three-pane workbench:

```tsx
<div className="app-shell">
  <header className="topbar">...</header>
  <aside className="left-rail" aria-label="Knowledge Vault">...</aside>
  <main className="main-pane">...</main>
  <aside className="right-rail" aria-label="Note metadata">...</aside>
</div>
```

**Planning guidance**

- Extend this workbench instead of creating a landing page.
- First viewport must show URL submission and current/empty job state.
- Right rail should show job metadata, artifact counts, provenance, and selected claim/screenshot details.

### Navigation and Data Shape

**Likely files**

- `frontend/src/data/sampleVault.ts`
- `frontend/src/api/ingestion.ts`
- `frontend/src/types/ingestion.ts`

**Closest existing analog**

- `sampleVault.ts` defines typed data and lucide icons for vault sections:

```ts
export type VaultSectionName =
  | "Videos"
  | "Creators"
  | "Claims"
  | "Papers"
```

**Planning guidance**

- Add typed ingestion DTOs rather than using `any`.
- Keep UI components TikTok-agnostic after the submission boundary; they should render normalized job/artifact/claim/triage objects.

### Styling

**Likely files**

- `frontend/src/styles/app.css`
- `frontend/src/styles/tokens.css`

**Closest existing analog**

- Existing tokens define colors, spacing, rails, and typography:

```css
:root {
  --color-bg: #f8faf7;
  --color-surface: #ffffff;
  --color-accent: #256f62;
  --color-evidence: #8a5a00;
  --space-xs: 4px;
  --space-sm: 8px;
}
```

**Planning guidance**

- Reuse existing tokens and approved `02-UI-SPEC.md` constraints.
- Do not introduce a new palette.
- Keep 8px max radius.
- Use fixed 16:9 screenshot thumbnails to avoid layout shift.
- Use `aria-live="polite"` for progress and `role="alert"` for blocking errors.

## Test Patterns

### Backend

**Closest existing analogs**

- `backend/tests/test_schemas.py`
- `backend/tests/test_contracts.py`

**Planning guidance**

- Add focused tests for:
  - schema enums and DTO validation
  - URL validation
  - compliance default-deny behavior
  - timestamped transcript segment parsing
  - untrusted wrapper use before extraction
  - claim parse failures
  - research-basis triage statuses
  - vault/MongoDB persistence shape

### Frontend

**Closest existing setup**

- `frontend/package.json` defines `vitest`.

**Planning guidance**

- If component tests are added, keep them focused on form submission, progress states, artifact rendering, recoverable errors, and triage copy.
- If the current test setup lacks DOM testing helpers, either add them explicitly or keep frontend verification to `yarn build` plus typed component fixtures.

## Planning Implications

- Wave 1 should close contracts/schemas and the transcript/screenshot vault gap before persistence/UI depend on them.
- Backend services can be split from UI work where DTOs are stable.
- Live TikTok/OpenAI/media work should have fixture-backed paths and mockable adapters so execution can complete without platform/network access.
- Full paper discovery, evidence evaluation, ratings, and graph UI are out of scope for Phase 2.
