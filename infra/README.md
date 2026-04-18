# Local Infrastructure

Phase 1 runs datastores only in Docker Compose. The backend and frontend run on the host during development.
MongoDB is exposed only to the Compose network to avoid conflicting with a local host MongoDB.

## Start Datastores

From this directory:

```bash
docker compose --env-file ../.env.example up -d
```

## Check Status

```bash
docker compose ps
```

## Stop Datastores

```bash
docker compose down
```

## Delete Local Datastore Volumes

```bash
docker compose down -v
```

Warning: `docker compose down -v` deletes the local MongoDB and Qdrant volumes.
