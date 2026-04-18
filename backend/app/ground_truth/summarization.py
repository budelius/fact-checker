import json
from uuid import UUID, uuid5

from openai import OpenAI

from app.safety.input_boundaries import wrap_untrusted_text
from app.schemas.ground_truth import PaperChunk, PaperMetadata, PaperSummary
from app.settings import Settings


def build_paper_summary_prompt(metadata: PaperMetadata, chunks: list[PaperChunk]) -> str:
    wrapped_chunks = "\n\n".join(
        wrap_untrusted_text(f"paper_chunk:{chunk.chunk_id}", chunk.text) for chunk in chunks
    )
    return (
        "Summarize this AI research paper as strict JSON with fields "
        "`summary_markdown`, `methods`, `key_claims`, `limitations`, `references`, and `provenance`.\n"
        f"Title: {metadata.title}\n"
        f"Abstract: {metadata.abstract or 'Not available.'}\n\n"
        f"{wrapped_chunks}"
    )


def parse_paper_summary_response(raw: str, paper_uuid: UUID) -> PaperSummary:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    payload = json.loads(cleaned)
    payload["paper_uuid"] = str(paper_uuid)
    return PaperSummary.model_validate(payload)


def summarize_without_provider(metadata: PaperMetadata, chunks: list[PaperChunk]) -> PaperSummary:
    first_chunk = chunks[0].text if chunks else ""
    summary_bits = [f"## Summary\n{metadata.title}"]
    if metadata.abstract:
        summary_bits.append(metadata.abstract)
    if first_chunk:
        summary_bits.append(first_chunk[:500])
    return PaperSummary(
        uuid=uuid5(metadata.uuid, "summary:deterministic_fallback"),
        paper_uuid=metadata.uuid,
        summary_markdown="\n\n".join(summary_bits),
        methods=[],
        key_claims=[metadata.abstract] if metadata.abstract else [],
        limitations=["Deterministic fallback summary; provider summary not used."],
        references=metadata.source_links,
        provenance={"mode": "deterministic_fallback", "chunk_count": len(chunks)},
    )


class PaperSummarizer:
    def __init__(self, settings: Settings, client: OpenAI | None = None) -> None:
        self.settings = settings
        self.client = client

    def summarize(self, metadata: PaperMetadata, chunks: list[PaperChunk]) -> PaperSummary:
        if self.client is None:
            return summarize_without_provider(metadata, chunks)

        response = self.client.responses.create(
            model=self.settings.openai_summary_model,
            input=build_paper_summary_prompt(metadata, chunks),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "paper_summary",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary_markdown": {"type": "string"},
                            "methods": {"type": "array", "items": {"type": "string"}},
                            "key_claims": {"type": "array", "items": {"type": "string"}},
                            "limitations": {"type": "array", "items": {"type": "string"}},
                            "references": {"type": "array", "items": {"type": "string"}},
                            "provenance": {"type": "object"},
                        },
                        "required": [
                            "summary_markdown",
                            "methods",
                            "key_claims",
                            "limitations",
                            "references",
                            "provenance",
                        ],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            },
        )
        return parse_paper_summary_response(response.output_text, metadata.uuid)
