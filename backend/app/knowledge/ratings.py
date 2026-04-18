from pathlib import Path
from uuid import UUID

import yaml

from app.schemas.ratings import RatingBadge, RatingConfidence, RatingRecord, RatingTargetType

MIN_NON_EXPERIMENTAL_EVIDENCE = 10
STRONG_SUPPORTED_RATIO = 0.75
MAX_STRONG_CONTRADICTED_RATIO = 0.10
MIXED_SIGNAL_RATIO = 0.20

LABELS = ("supported", "contradicted", "mixed", "insufficient")


def _value(payload, key: str, default=None):
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _normalize_label_counts(raw_counts) -> dict[str, int]:
    counts = {label: 0 for label in LABELS}
    for key, value in (raw_counts or {}).items():
        label = getattr(key, "value", key)
        if label in counts:
            counts[str(label)] += int(value)
    return counts


def _rating_badge(counts: dict[str, int], evidence_count: int) -> RatingBadge:
    if evidence_count == 0:
        return RatingBadge.insufficient_history
    if evidence_count < MIN_NON_EXPERIMENTAL_EVIDENCE:
        return RatingBadge.limited_evidence

    contradicted_ratio = counts["contradicted"] / evidence_count
    mixed_ratio = counts["mixed"] / evidence_count
    supported_ratio = counts["supported"] / evidence_count
    if contradicted_ratio > MIXED_SIGNAL_RATIO or mixed_ratio > MIXED_SIGNAL_RATIO:
        return RatingBadge.mixed_evidence_history
    if (
        supported_ratio >= STRONG_SUPPORTED_RATIO
        and contradicted_ratio <= MAX_STRONG_CONTRADICTED_RATIO
    ):
        return RatingBadge.strong_evidence_history
    return RatingBadge.mixed_evidence_history


def _confidence(badge: RatingBadge, experimental: bool) -> RatingConfidence:
    if experimental:
        return RatingConfidence.low
    if badge == RatingBadge.strong_evidence_history:
        return RatingConfidence.high
    return RatingConfidence.medium


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def build_rating_record(target_entity, reports, relationships) -> RatingRecord:
    target_uuid = UUID(str(_value(target_entity, "uuid")))
    target_entity_type = RatingTargetType(str(_value(target_entity, "entity_type")))
    target_title = str(_value(target_entity, "title", target_uuid))

    label_distribution = {label: 0 for label in LABELS}
    report_version_uuids = []
    evidence_uuids = []
    source_basis = []
    for report in reports or []:
        counts = _normalize_label_counts(_value(report, "label_counts", {}))
        for label, count in counts.items():
            label_distribution[label] += count
        report_uuid = _value(report, "report_uuid")
        if report_uuid:
            report_version_uuids.append(UUID(str(report_uuid)))
        evidence_uuids.extend(UUID(str(value)) for value in _value(report, "cited_evidence_uuids", []))
        markdown_path = _value(report, "markdown_path")
        if markdown_path:
            source_basis.append(str(markdown_path))

    relationship_uuids = [
        UUID(str(_value(relationship, "uuid")))
        for relationship in relationships or []
        if _value(relationship, "uuid")
    ]
    evidence_count = sum(label_distribution.values())
    badge = _rating_badge(label_distribution, evidence_count)
    experimental = evidence_count < MIN_NON_EXPERIMENTAL_EVIDENCE
    vault_path = f"vault/wiki/ratings/{target_entity_type.value}-{_slug(target_title)}.md"
    return RatingRecord(
        target_uuid=target_uuid,
        target_entity_type=target_entity_type,
        target_title=target_title,
        badge=badge,
        experimental=experimental,
        evidence_count=evidence_count,
        label_distribution=label_distribution,
        source_basis=source_basis,
        confidence_level=_confidence(badge, experimental),
        report_version_uuids=report_version_uuids,
        evidence_uuids=evidence_uuids,
        relationship_uuids=relationship_uuids,
        vault_path=vault_path,
    )


def write_rating_markdown(record: RatingRecord, vault_root: Path) -> Path:
    filename = Path(record.vault_path).name
    output_dir = vault_root / "wiki" / "ratings"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    frontmatter = yaml.safe_dump(
        {
            "uuid": str(record.rating_uuid),
            "entity_type": "rating",
            "target_uuid": str(record.target_uuid),
            "target_entity_type": record.target_entity_type.value,
            "badge": record.badge.value,
            "experimental": record.experimental,
            "vault_path": record.vault_path,
            "generated_at": record.generated_at.isoformat(),
        },
        sort_keys=False,
    ).strip()
    report_lines = [f"- {uuid}" for uuid in record.report_version_uuids] or ["- None"]
    body = "\n".join(
        [
            f"# {record.target_title} rating",
            "",
            "## Evidence count",
            "",
            str(record.evidence_count),
            "",
            "## Label distribution",
            "",
            *[f"- {label}: {count}" for label, count in record.label_distribution.items()],
            "",
            "## Source basis",
            "",
            *[f"- {source}" for source in record.source_basis or ["No report versions yet."]],
            "",
            "## Confidence level",
            "",
            record.confidence_level.value,
            "",
            "## Report versions",
            "",
            *report_lines,
            "",
        ]
    )
    output_path.write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
    return output_path
