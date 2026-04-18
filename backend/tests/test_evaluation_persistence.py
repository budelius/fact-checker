from uuid import uuid4

from app.evaluation.evaluator import citation_from_candidate
from app.evaluation.persistence import persist_report_knowledge
from app.evaluation.versioning import build_report_version_identity, rerun_available
from app.schemas.evaluation import ClaimEvaluation, EvaluationLabel, EvidenceCandidate, ReportVersion
from app.schemas.relationships import RelationshipType


class FakeRepository:
    def __init__(self) -> None:
        self.entities = []
        self.relationships = []

    def upsert_entity(self, entity) -> None:
        self.entities.append(entity)

    def upsert_relationship(self, relationship) -> None:
        self.relationships.append(relationship)


def _candidate(claim_uuid):
    return EvidenceCandidate(
        claim_uuid=claim_uuid,
        evidence_uuid=uuid4(),
        title="Attention Is All You Need",
        raw_text="The Transformer allows significantly more parallelization.",
        source_url="https://arxiv.org/abs/1706.03762",
        chunk_id="chunk-1",
    )


def _report_with_label(label: EvaluationLabel) -> ReportVersion:
    claim_uuid = uuid4()
    candidate = _candidate(claim_uuid)
    citations = [] if label == EvaluationLabel.insufficient else [citation_from_candidate(candidate)]
    evaluation = ClaimEvaluation(
        claim_uuid=claim_uuid,
        claim_text="Transformers parallelize sequence modeling.",
        label=label,
        rationale="Evaluation rationale.",
        citations=citations,
        uncertainty_note="No direct evidence." if label == EvaluationLabel.insufficient else None,
    )
    return ReportVersion(
        markdown_path="vault/wiki/reports/attention-report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        claim_uuids=[claim_uuid],
        cited_evidence_uuids=[candidate.evidence_uuid] if citations else [],
        candidate_evidence_uuids=[candidate.uuid],
        label_counts={label: 1},
        narrative_markdown="Narrative report.",
        evaluations=[evaluation],
        cited_evidence=citations,
    )


def test_report_version_identity_creates_distinct_rerun_paths():
    ingestion_job_uuid = uuid4()
    ground_truth_job_uuid = uuid4()

    first_identity = build_report_version_identity(
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        title="attention report",
    )
    first_report = ReportVersion(
        report_uuid=first_identity.report_uuid,
        report_group_uuid=first_identity.report_group_uuid,
        version=first_identity.version,
        markdown_path=first_identity.markdown_path,
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        narrative_markdown="First version.",
    )
    second_identity = build_report_version_identity(
        ingestion_job_uuid=ingestion_job_uuid,
        ground_truth_job_uuid=ground_truth_job_uuid,
        previous_versions=[first_report],
        title="attention report",
    )

    assert first_identity.version == 1
    assert second_identity.version == 2
    assert first_identity.report_group_uuid == second_identity.report_group_uuid
    assert first_identity.report_uuid != second_identity.report_uuid
    assert first_identity.markdown_path != second_identity.markdown_path
    assert first_report.markdown_path == first_identity.markdown_path


def test_rerun_available_when_new_evidence_chunk_appears():
    known_evidence_uuid = uuid4()
    new_evidence_uuid = uuid4()
    report = ReportVersion(
        markdown_path="vault/wiki/reports/report-v1.md",
        ingestion_job_uuid=uuid4(),
        ground_truth_job_uuid=uuid4(),
        narrative_markdown="First version.",
        candidate_evidence_uuids=[known_evidence_uuid],
    )

    assert rerun_available(report, [known_evidence_uuid]) is False
    assert rerun_available(report, [known_evidence_uuid, new_evidence_uuid]) is True


def test_persist_report_writes_markdown_and_report_entity(tmp_path):
    repository = FakeRepository()
    report = _report_with_label(EvaluationLabel.supported)

    result = persist_report_knowledge(repository, tmp_path / "vault", report)

    assert result["markdown_files"] == 1
    assert (tmp_path / "vault" / "wiki" / "reports" / "attention-report-v1.md").exists()
    assert repository.entities[0].uuid == report.report_uuid
    assert repository.entities[0].entity_type.value == "report"


def test_supported_labels_create_support_relationships(tmp_path):
    repository = FakeRepository()

    persist_report_knowledge(repository, tmp_path / "vault", _report_with_label(EvaluationLabel.supported))

    relationship_types = {relationship.relationship_type for relationship in repository.relationships}
    assert RelationshipType.supports in relationship_types
    assert RelationshipType.contradicts not in relationship_types


def test_contradicted_labels_create_contradict_relationships(tmp_path):
    repository = FakeRepository()

    persist_report_knowledge(
        repository,
        tmp_path / "vault",
        _report_with_label(EvaluationLabel.contradicted),
    )

    relationship_types = {relationship.relationship_type for relationship in repository.relationships}
    assert RelationshipType.contradicts in relationship_types
    assert RelationshipType.supports not in relationship_types


def test_mixed_labels_do_not_create_misleading_support_or_contradict_edges(tmp_path):
    repository = FakeRepository()

    persist_report_knowledge(repository, tmp_path / "vault", _report_with_label(EvaluationLabel.mixed))

    relationship_types = {relationship.relationship_type for relationship in repository.relationships}
    assert RelationshipType.cites in relationship_types
    assert RelationshipType.supports not in relationship_types
    assert RelationshipType.contradicts not in relationship_types


def test_insufficient_labels_do_not_create_support_or_contradict_edges(tmp_path):
    repository = FakeRepository()

    persist_report_knowledge(
        repository,
        tmp_path / "vault",
        _report_with_label(EvaluationLabel.insufficient),
    )

    relationship_types = {relationship.relationship_type for relationship in repository.relationships}
    assert RelationshipType.discussed_in in relationship_types
    assert RelationshipType.supports not in relationship_types
    assert RelationshipType.contradicts not in relationship_types
