# fact-checker

Fact Checker is a user-owned AI research fact-checking system. It is designed to gather ground truth, keep evidence in an owned Markdown vault, and build searchable store contracts for later fact-checking workflows.

## Local development

Phase 1 uses a monorepo layout:

- `backend/` - FastAPI service and storage contracts
- `frontend/` - React, TypeScript, Vite, and Yarn knowledge-browser shell
- `vault/` - Obsidian-compatible Markdown knowledge base
- `infra/` - local Docker Compose services and infrastructure notes

Docker Compose runs MongoDB and Qdrant only by default. Backend and frontend processes run on the host during development.

```bash
cd infra
docker compose --env-file ../.env.example up -d
```

Use a local `.env` for real credentials. Do not commit API keys, provider tokens, or private source material.
