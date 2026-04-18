import {
  API_BASE_URL,
  type JobLifecycleStatus,
  type StageStatus,
} from "./ingestion";

export type CandidateStatus =
  | "selected_ground_truth"
  | "rejected"
  | "supplemental"
  | "no_paper_found"
  | "needs_manual_review";

export type CandidateKind = "paper" | "preprint" | "non_paper" | "unknown";

export type GroundTruthStage = {
  name: string;
  status: StageStatus;
  message?: string | null;
  event_uuid?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
};

export type GroundTruthArtifact = {
  uuid: string;
  artifact_type: string;
  vault_path?: string | null;
  source_url?: string | null;
  metadata: Record<string, unknown>;
};

export type ExternalPaperId = {
  provider: string;
  value: string;
};

export type PaperAuthor = {
  name: string;
  external_ids: ExternalPaperId[];
};

export type PaperCandidate = {
  uuid: string;
  title: string;
  kind: CandidateKind;
  status: CandidateStatus;
  external_ids: ExternalPaperId[];
  authors: PaperAuthor[];
  abstract?: string | null;
  publication_date?: string | null;
  source_url?: string | null;
  pdf_url?: string | null;
  landing_page_url?: string | null;
  confidence?: number | null;
  selected_reason?: string | null;
  rejected_reason?: string | null;
};

export type SourceDecision = {
  uuid: string;
  claim_uuid?: string | null;
  candidate_uuid?: string | null;
  status: CandidateStatus;
  reason: string;
  provenance: Record<string, unknown>;
};

export type PaperMetadata = {
  uuid: string;
  title: string;
  authors: PaperAuthor[];
  external_ids: ExternalPaperId[];
  publication_status: string;
  publication_date?: string | null;
  abstract?: string | null;
  source_links: string[];
  pdf_url?: string | null;
  vault_path?: string | null;
  processing_status: string;
};

export type PaperChunk = {
  uuid: string;
  paper_uuid: string;
  source_uuid: string;
  chunk_id: string;
  text: string;
  page_start?: number | null;
  page_end?: number | null;
  section?: string | null;
  vault_path: string;
  source_url: string;
};

export type PaperSummary = {
  uuid: string;
  paper_uuid: string;
  summary_markdown: string;
  methods: string[];
  key_claims: string[];
  limitations: string[];
  references: string[];
  provenance: Record<string, unknown>;
};

export type GroundTruthJob = {
  job_uuid: string;
  ingestion_job_uuid: string;
  status: JobLifecycleStatus;
  current_operation: string;
  stages: GroundTruthStage[];
  artifacts: GroundTruthArtifact[];
  candidates: PaperCandidate[];
  decisions: SourceDecision[];
  papers: PaperMetadata[];
  chunks: PaperChunk[];
  summaries: PaperSummary[];
  created_at: string;
  updated_at: string;
  error_message?: string | null;
};

async function parseResponse<T>(response: Response, fallbackError: string): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(typeof payload.detail === "string" ? payload.detail : fallbackError);
  }

  return response.json() as Promise<T>;
}

export async function startGroundTruthJobFromIngestion(
  ingestionJobUuid: string,
): Promise<GroundTruthJob> {
  return parseResponse<GroundTruthJob>(
    await fetch(`${API_BASE_URL}/ground-truth/jobs/from-ingestion/${ingestionJobUuid}`, {
      method: "POST",
    }),
    "ground_truth_request_failed",
  );
}

export async function fetchGroundTruthJob(jobUuid: string): Promise<GroundTruthJob> {
  return parseResponse<GroundTruthJob>(
    await fetch(`${API_BASE_URL}/ground-truth/jobs/${jobUuid}`),
    "ground_truth_fetch_failed",
  );
}
