from collections.abc import Callable, Iterable
from uuid import UUID

from app.ground_truth.dedupe import merge_candidates
from app.ground_truth.progress import build_ground_truth_event
from app.ground_truth.queries import build_discovery_queries
from app.ground_truth.selection import select_ground_truth_for_claim
from app.schemas.claims import ExtractedClaim
from app.schemas.ground_truth import (
    CandidateStatus,
    GroundTruthJob,
    GroundTruthStage,
    GroundTruthStageName,
    PaperCandidate,
)
from app.schemas.ingestion import (
    JobLifecycleStatus,
    ResearchBasisTriage,
    ScreenshotArtifact,
    StageStatus,
)

TraceSink = Callable[[dict[str, str | None]], None]


class GroundTruthDiscoveryService:
    def __init__(
        self,
        openai_web_client: object | None = None,
        paper_index_clients: Iterable[object] | None = None,
        trace_sink: TraceSink | None = None,
    ) -> None:
        self.openai_web_client = openai_web_client
        self.paper_index_clients = list(paper_index_clients or [])
        self.trace_sink = trace_sink

    def _record(
        self,
        job: GroundTruthJob,
        stage: GroundTruthStageName,
        status: StageStatus,
        message: str,
        entity_uuid: UUID | None = None,
    ) -> None:
        job.stages.append(
            GroundTruthStage(
                name=stage,
                status=status,
                message=message,
                event_uuid=entity_uuid,
            )
        )
        event = build_ground_truth_event(
            job.job_uuid,
            stage.value,
            status.value,
            message,
            entity_uuid=entity_uuid,
        )
        if self.trace_sink:
            self.trace_sink(event)

    def _provider_name(self, client: object) -> str:
        return str(getattr(client, "provider", None) or client.__class__.__name__)

    def _search_provider(self, client: object, query) -> tuple[list[PaperCandidate], str | None]:
        try:
            return list(client.search(query)), None
        except Exception as exc:
            provider = self._provider_name(client)
            return [], f"{provider}:{exc.__class__.__name__}"

    def _stage_message(self, base: str, failures: list[str]) -> str:
        if not failures:
            return base

        unique_failures = sorted(set(failures))
        preview = ", ".join(unique_failures[:3])
        suffix = f" Source provider limits/errors: {preview}."
        if len(unique_failures) > 3:
            suffix = f" Source provider limits/errors: {preview}, and {len(unique_failures) - 3} more."
        return f"{base}{suffix}"

    def run_for_ingestion_payload(self, ingestion_payload: dict) -> GroundTruthJob:
        ingestion_job_uuid = UUID(str(ingestion_payload["job_uuid"]))
        job = GroundTruthJob(
            ingestion_job_uuid=ingestion_job_uuid,
            status=JobLifecycleStatus.running,
            current_operation="Searching for paper candidates.",
        )

        claims = [ExtractedClaim.model_validate(claim) for claim in ingestion_payload.get("claims", [])]
        research_basis_payload = ingestion_payload.get("research_basis") or {
            "status": "no_research_source_found",
            "reason": "No research basis in ingestion payload.",
            "candidates": [],
        }
        research_basis = ResearchBasisTriage.model_validate(research_basis_payload)
        screenshots = [
            ScreenshotArtifact.model_validate(screenshot)
            for screenshot in ingestion_payload.get("screenshots", [])
        ]
        self._record(job, GroundTruthStageName.load_claims, StageStatus.succeeded, "Loaded claims.")

        queries = build_discovery_queries(claims, research_basis, screenshots)
        self._record(
            job,
            GroundTruthStageName.generate_queries,
            StageStatus.succeeded,
            f"Generated {len(queries)} discovery queries.",
        )

        raw_candidates: list[PaperCandidate] = []
        openai_failures: list[str] = []
        if self.openai_web_client:
            for query in queries:
                candidates, failure = self._search_provider(self.openai_web_client, query)
                raw_candidates.extend(candidates)
                if failure:
                    openai_failures.append(failure)
        self._record(
            job,
            GroundTruthStageName.search_openai_web,
            StageStatus.succeeded if self.openai_web_client else StageStatus.skipped,
            self._stage_message("search_openai_web completed.", openai_failures),
        )

        paper_index_failures: list[str] = []
        for query in queries:
            for client in self.paper_index_clients:
                candidates, failure = self._search_provider(client, query)
                raw_candidates.extend(candidates)
                if failure:
                    paper_index_failures.append(failure)
        self._record(
            job,
            GroundTruthStageName.search_paper_indexes,
            StageStatus.succeeded if self.paper_index_clients else StageStatus.skipped,
            self._stage_message("search_paper_indexes completed.", paper_index_failures),
        )

        job.candidates = merge_candidates(raw_candidates)
        self._record(
            job,
            GroundTruthStageName.merge_candidates,
            StageStatus.succeeded,
            f"Merged {len(raw_candidates)} candidates into {len(job.candidates)} candidates.",
        )

        for claim in claims:
            job.decisions.extend(select_ground_truth_for_claim(claim.uuid, job.candidates))
        has_selected = any(
            decision.status == CandidateStatus.selected_ground_truth for decision in job.decisions
        )
        job.current_operation = (
            "Paper candidates selected for processing."
            if has_selected
            else "No scientific evidence found for now."
        )
        job.status = JobLifecycleStatus.succeeded
        self._record(
            job,
            GroundTruthStageName.select_sources,
            StageStatus.succeeded,
            job.current_operation,
        )
        return job
