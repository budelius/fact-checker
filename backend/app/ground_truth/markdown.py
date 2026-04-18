from datetime import UTC, datetime
from uuid import UUID

import yaml

from app.ingestion.persistence import slugify
from app.schemas.ground_truth import PaperMetadata, PaperSummary, SourceDecision


def paper_slug(metadata: PaperMetadata) -> str:
    return slugify(metadata.title)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _frontmatter(
    metadata: PaperMetadata,
    related_claim_uuids: list[UUID],
) -> dict:
    slug = paper_slug(metadata)
    now = _now_iso()
    aliases = [external_id.value for external_id in metadata.external_ids]
    relationships = [{"type": "related_to", "target_uuid": str(uuid)} for uuid in related_claim_uuids]
    return {
        "uuid": str(metadata.uuid),
        "entity_type": "paper",
        "slug": slug,
        "title": metadata.title,
        "aliases": aliases,
        "external_ids": [external_id.model_dump(mode="json") for external_id in metadata.external_ids],
        "relationships": relationships,
        "created_at": now,
        "updated_at": now,
    }


def _list_lines(values: list[str]) -> str:
    if not values:
        return "- Not extracted yet."
    return "\n".join(f"- {value}" for value in values)


def _decision_lines(decisions: list[SourceDecision]) -> str:
    if not decisions:
        return "- No source decisions recorded."
    return "\n".join(
        f"- `{decision.status.value}`: {decision.reason}"
        + (f" (claim: `{decision.claim_uuid}`)" if decision.claim_uuid else "")
        for decision in decisions
    )


def build_paper_markdown(
    metadata: PaperMetadata,
    summary: PaperSummary | None,
    related_claim_uuids: list[UUID],
    decisions: list[SourceDecision],
) -> str:
    frontmatter = yaml.safe_dump(
        _frontmatter(metadata, related_claim_uuids),
        sort_keys=False,
        allow_unicode=False,
    ).strip()
    source_links = metadata.source_links or [metadata.pdf_url] if metadata.pdf_url else metadata.source_links
    abstract = metadata.abstract or "Not available."

    methods = summary.methods if summary else []
    key_claims = summary.key_claims if summary else []
    limitations = summary.limitations if summary else []
    references = summary.references if summary else []
    summary_markdown = summary.summary_markdown if summary else "Summary not generated yet."

    return "\n".join(
        [
            "---",
            frontmatter,
            "---",
            "",
            f"# {metadata.title}",
            "",
            summary_markdown,
            "",
            "## Source Links",
            _list_lines([link for link in source_links if link]),
            "",
            "## Abstract",
            abstract,
            "",
            "## Methods",
            _list_lines(methods),
            "",
            "## Key Claims",
            _list_lines(key_claims),
            "",
            "## Limitations",
            _list_lines(limitations),
            "",
            "## References",
            _list_lines(references),
            "",
            "## Provenance",
            _decision_lines(decisions),
            "",
        ]
    )
