from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid5

from app.evaluation.markdown import build_report_markdown
from app.ingestion.persistence import slugify
from app.schemas.entities import EntityType, KnowledgeEntity
from app.schemas.evaluation import EvaluationLabel, ReportVersion
from app.schemas.relationships import KnowledgeRelationship, RelationshipType


def _now() -> datetime:
    return datetime.now(UTC)


def _slug_from_markdown_path(markdown_path: str) -> str:
    return Path(markdown_path).stem or slugify(f"report-{datetime.now(UTC).timestamp()}")


def _vault_note_path(vault_root: Path, markdown_path: str) -> Path:
    normalized = markdown_path.removeprefix("vault/")
    return vault_root / normalized


def _report_entity(report: ReportVersion) -> KnowledgeEntity:
    slug = _slug_from_markdown_path(report.markdown_path)
    now = _now()
    return KnowledgeEntity(
        uuid=report.report_uuid,
        entity_type=EntityType.report,
        slug=slug,
        title=f"Fact-check report v{report.version}",
        vault_path=report.markdown_path,
        aliases=[str(report.report_group_uuid)],
        external_ids=[],
        created_at=now,
        updated_at=now,
    )


def _relationship(
    relationship_type: RelationshipType,
    source_uuid: UUID,
    target_uuid: UUID,
    provenance: str,
) -> KnowledgeRelationship:
    return KnowledgeRelationship(
        uuid=uuid5(source_uuid, f"{relationship_type.value}:{target_uuid}:{provenance}"),
        relationship_type=relationship_type,
        source_uuid=source_uuid,
        target_uuid=target_uuid,
        provenance=provenance,
        created_at=_now(),
    )


def _claim_relationship_type(label: EvaluationLabel) -> RelationshipType | None:
    if label == EvaluationLabel.supported:
        return RelationshipType.supports
    if label == EvaluationLabel.contradicted:
        return RelationshipType.contradicts
    if label == EvaluationLabel.mixed:
        return RelationshipType.cites
    return None


def persist_report_knowledge(repository, vault_root: Path, report: ReportVersion) -> dict[str, int]:
    markdown = build_report_markdown(report)
    note_path = _vault_note_path(vault_root, report.markdown_path)
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(markdown, encoding="utf-8")

    entity_count = 0
    relationship_count = 0
    repository.upsert_entity(_report_entity(report))
    entity_count += 1

    cited_report_edges: set[UUID] = set()
    for evaluation in report.evaluations:
        repository.upsert_relationship(
            _relationship(
                RelationshipType.discussed_in,
                evaluation.claim_uuid,
                report.report_uuid,
                f"phase-4-evaluation:v{report.version}",
            )
        )
        relationship_count += 1
        claim_relationship_type = _claim_relationship_type(evaluation.label)
        for citation in evaluation.citations:
            if citation.evidence_uuid not in cited_report_edges:
                repository.upsert_relationship(
                    _relationship(
                        RelationshipType.cites,
                        report.report_uuid,
                        citation.evidence_uuid,
                        f"phase-4-evaluation:v{report.version}",
                    )
                )
                cited_report_edges.add(citation.evidence_uuid)
                relationship_count += 1
            if claim_relationship_type is None:
                continue
            provenance_label = (
                f"phase-4-evaluation:{evaluation.label.value}:v{report.version}"
            )
            repository.upsert_relationship(
                _relationship(
                    claim_relationship_type,
                    evaluation.claim_uuid,
                    citation.evidence_uuid,
                    provenance_label,
                )
            )
            relationship_count += 1

    return {"entities": entity_count, "relationships": relationship_count, "markdown_files": 1}
