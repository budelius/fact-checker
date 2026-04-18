I want to build a fact checker tool, mainly to save time on checking facts and storing them as Markdown to build a knowledge graph for future fact-checking improvements.

The focus will be on gathering ground truth and organizing knowledge to improve fact checking.

Ground truth is defined by links to research papers, or in some cases news articles.

A challenge will be finding the right paper — specifically the paper that is the topic of a creator's TikTok (or maybe Instagram) video.

The narrow use case will be checking facts in the AI research space by analysing TikTok video links (transcripts and video content).

Add them to a Markdown database or UI analogous to Obsidian, and a vector storage for search.

So the user will post a link on a website for now (later into a chat client or into OpenClaw).

The backend will do the research. For that we:

- Download the public video
- Download the transcript, or transcribe
- Fact-check by doing a search with the OpenAI API (preferably live search)
- Find research paper links, download them, index them in a vector database (Qdrant)
- Summarize the paper as Markdown together with links and possibly further references
- Add the transcript and some screenshots as well
- Judge the truth of the paper by comparing against the transcript
- Rate the creators in general and the authors of the papers
- Combine and build a knowledge graph with a Markdown viewer/database (Obsidian-like), a vector database (Qdrant), and a graph database (to be chosen)
- Rate creators, authors, papers, and sources — building a knowledge graph that indirectly helps rate truth

Future outlook: use smart glasses like Meta Ray-Ban and their streaming SDK to watch videos and fact-check them in real time, or use that as a fact checker / knowledge-graph assistant in meetings.

## Why not ChatGPT?

- Vendor lock-in
- Non-EU
- Create awareness of hallucinations
- Have a second opinion

The general hybrid approach — combining LLMs with a self-building knowledge graph — is the key to providing accuracy. And most importantly, we make sure the knowledge is owned by the user or the company.

## It's not just owning your evidence — it's owning the knowledge behind it

We build a knowledge base for you — your personal brain. Because we use an easily human-readable knowledge graph (Markdown notes with links), we can check facts more easily: graph connections give us a **second measurement** alongside paper-level evidence. We are transparent because everything is Markdown you can read and edit, while still building up a custom brain. Like Notion — self-owned and extensible.
