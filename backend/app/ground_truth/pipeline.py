from pathlib import Path

from app.contracts.vault import expected_wiki_path
from app.ground_truth.acquisition import acquire_paper_pdf
from app.ground_truth.chunking import chunk_parsed_paper
from app.ground_truth.discovery import GroundTruthDiscoveryService
from app.ground_truth.indexing import EmbeddingProvider, index_paper_chunks, index_paper_summaries
from app.ground_truth.markdown import paper_slug
from app.ground_truth.parsing import parse_pdf_to_pages
from app.ground_truth.persistence import persist_paper_knowledge
from app.ground_truth.summarization import PaperSummarizer, summarize_without_provider
from app.schemas.ground_truth import (
    CandidateStatus,
    PaperCandidate,
    PaperMetadata,
    PaperProcessingStatus,
)
from app.settings import Settings


class GroundTruthPipeline:
    def __init__(
        self,
        discovery_service: GroundTruthDiscoveryService,
        settings: Settings,
        acquisition_client: object | None = None,
        summarizer: PaperSummarizer | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.discovery_service = discovery_service
        self.settings = settings
        self.acquisition_client = acquisition_client
        self.summarizer = summarizer
        self.embedding_provider = embedding_provider

    def _metadata_from_candidate(self, candidate: PaperCandidate) -> PaperMetadata:
        return PaperMetadata(
            uuid=candidate.uuid,
            title=candidate.title,
            authors=candidate.authors,
            external_ids=candidate.external_ids,
            publication_status=candidate.kind.value,
            publication_date=candidate.publication_date,
            abstract=candidate.abstract,
            source_links=[
                link
                for link in [candidate.source_url, candidate.landing_page_url, candidate.pdf_url]
                if link
            ],
            pdf_url=candidate.pdf_url,
            processing_status=PaperProcessingStatus.metadata_only,
        )

    def _absolute_raw_path(self, vault_root: Path, raw_pdf_path: str | None) -> Path | None:
        if not raw_pdf_path:
            return None
        normalized = raw_pdf_path.removeprefix("vault/")
        return vault_root / normalized

    def run_from_ingestion_payload(
        self,
        ingestion_payload: dict,
        repository,
        qdrant_repository,
        vault_root: Path,
    ):
        job = self.discovery_service.run_for_ingestion_payload(ingestion_payload)
        selected_candidate_uuids = {
            decision.candidate_uuid
            for decision in job.decisions
            if decision.status == CandidateStatus.selected_ground_truth
            and decision.candidate_uuid is not None
        }
        if not selected_candidate_uuids:
            job.current_operation = "No scientific evidence found for now."
            return job

        selected_candidates = [
            candidate for candidate in job.candidates if candidate.uuid in selected_candidate_uuids
        ]
        for candidate in selected_candidates:
            metadata = self._metadata_from_candidate(candidate)
            metadata.vault_path = expected_wiki_path("papers", paper_slug(metadata))
            acquisition = acquire_paper_pdf(
                candidate,
                vault_root,
                self.settings,
                client=self.acquisition_client,
            )
            metadata.processing_status = acquisition.status
            parsed_chunks = []
            pdf_path = self._absolute_raw_path(vault_root, acquisition.raw_pdf_path)
            if acquisition.status == PaperProcessingStatus.downloaded and pdf_path is not None:
                parsed = parse_pdf_to_pages(candidate.uuid, pdf_path)
                if parsed.status == PaperProcessingStatus.parsed:
                    metadata.processing_status = PaperProcessingStatus.parsed
                    parsed_chunks = chunk_parsed_paper(
                        candidate.uuid,
                        candidate.uuid,
                        parsed,
                        vault_path=metadata.vault_path,
                        source_url=candidate.source_url or candidate.pdf_url or "",
                    )

            summary = (
                self.summarizer.summarize(metadata, parsed_chunks)
                if self.summarizer
                else summarize_without_provider(metadata, parsed_chunks)
            )
            metadata.processing_status = PaperProcessingStatus.summarized
            persist_paper_knowledge(
                repository,
                vault_root,
                metadata,
                summary,
                parsed_chunks,
                job.decisions,
            )
            job.papers.append(metadata)
            job.chunks.extend(parsed_chunks)
            job.summaries.append(summary)

            if self.embedding_provider and qdrant_repository:
                relationship_uuids = [decision.uuid for decision in job.decisions]
                index_paper_chunks(
                    qdrant_repository,
                    self.embedding_provider,
                    parsed_chunks,
                    relationship_uuids,
                )
                index_paper_summaries(
                    qdrant_repository,
                    self.embedding_provider,
                    [summary],
                    {metadata.uuid: metadata},
                    {metadata.uuid: relationship_uuids},
                )

        job.current_operation = "Paper knowledge stored and indexed."
        return job
