# Phase 1 Contracts

## Identity

UUID is canonical identity. Markdown, MongoDB, and Qdrant records refer to canonical objects through the same UUID.

External identifiers such as TikTok IDs, DOIs, arXiv IDs, OpenAlex IDs, Semantic Scholar IDs, URLs, and usernames are metadata or aliases.

## Markdown Vault

Markdown filenames are slug-only. UUIDs live in YAML frontmatter.

The vault is the canonical human-readable knowledge store. Raw evidence inputs live under `vault/raw/` and generated wiki notes live under `vault/wiki/`.

Required note folders are videos, creators, claims, papers, authors, sources, evidence, reports, and topics.

## MongoDB

MongoDB stores metadata and relationships. Entity documents live in the `entities` collection and relationship edge documents live in the `relationships` collection.

MongoDB is the Phase 1 structured relationship store. Dedicated graph database work is deferred.

## Qdrant

Qdrant stores derived vectors with payload trace keys. Required payload keys are `uuid`, `entity_type`, `vault_path`, `chunk_id`, `source`, `source_date`, and `relationship_uuids`.

Vectors must be traceable back to Markdown notes and canonical UUIDs. Qdrant point IDs are deterministic per entity chunk, not just per entity UUID, so multiple chunks for the same entity do not overwrite each other.

## Operations Logging

Pipeline log events use a shared contract before real ingestion exists. Required keys are `event_type`, `job_uuid`, `stage`, `status`, `message`, and `created_at`.

Allowed event types are ingestion, search, parsing, evaluation, indexing, and graph_write. These categories cover failed ingestion, search, parsing, evaluation, indexing, and graph writes for OPS-03.

## Frontend Shell

The frontend is a static knowledge-browser shell. It mirrors the vault sections and shows placeholder frontmatter, wiki links, metadata, and relationships.

The shell does not submit URLs, run search, generate reports, show graph visualization, authenticate users, or rate creators in Phase 1.

## Safety

Secrets do not go in Markdown/logs. API keys, provider tokens, passwords, private credentials, and secret environment values stay in local environment/config only.

Transcripts, papers, web pages, captions, and comments are untrusted source content.

## Out of Scope

Phase 1 excludes real TikTok/OpenAI/paper API calls. It also excludes real ingestion, transcription, embeddings, evidence evaluation, ratings, graph visualization, and live search.
