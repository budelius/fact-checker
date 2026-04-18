# Fact Checker

**Fact Checker turns a public TikTok link into an evidence-backed research report — and builds your personal research brain in the process.**

## What it does

Paste a public TikTok URL. Fact Checker pulls the transcript and video context, isolates atomic AI-research claims, and finds the matching papers or preprints. Every claim lands with one of four cited labels — **supported**, **contradicted**, **mixed**, or **insufficient evidence** — and every label is traceable to the paper it came from. Creators, authors, papers, and sources get transparent ratings grounded in evidence history.

## Why another fact checker?

ChatGPT could answer. But it hallucinates. It's vendor-locked. It's non-EU. And nothing sticks — every conversation starts fresh.

Fact Checker is a **second opinion that remembers.**

## The real product is your knowledge, not the verdict

Every check writes into an owned, human-readable **Markdown knowledge graph** — videos, creators, claims, papers, authors, sources, and evidence, all linked. Because the graph is Markdown, you can inspect it, edit it, and open it in any editor. Because it's connected, **graph topology becomes a second signal for truth**: contradictions that span the brain catch what a single paper can't.

Like Notion. Like Obsidian. But it fact-checks itself.

## Principles

- **Owned** — Markdown files you keep, outside any chat-vendor's memory
- **Transparent** — every label cites the paper, author, and passage; no hidden truth score
- **EU-first** — durable knowledge stays outside OpenAI-hosted memory
- **Hybrid** — LLMs for extraction and summarization, the knowledge graph for long-term accuracy

## V1 scope

| | |
|---|---|
| **Input** | Public TikTok links |
| **Ground truth** | Research papers and preprints (arXiv, OpenAlex, Semantic Scholar) |
| **Surface** | Website with URL submission + Obsidian-like Markdown browser |
| **Storage** | Markdown vault (canonical) · MongoDB (entities + graph) · Qdrant (vector search) |

## Where it's going

TikTok AI-research fact-checking is the first narrow slice. As the brain grows, what's unlocked:

- Instagram and long-form video ingestion
- Chat-client and OpenClaw integrations
- Live fact-checking on smart glasses (Meta Ray-Ban streaming SDK)
- Meeting assistant with continuous evidence capture

## Built at stozn.ai

Part of the Stoz3n AI agent research lab. **Own your evidence. Own your brain.**
