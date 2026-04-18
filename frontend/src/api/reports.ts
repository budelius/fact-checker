import {
  API_BASE_URL,
  type JobLifecycleStatus,
  type StageStatus,
} from "./ingestion";

export type EvaluationLabel = "supported" | "contradicted" | "mixed" | "insufficient";
export type EvidenceSourceKind =
  | "paper_chunk"
  | "direct_source_text"
  | "news_article"
  | "paper_summary";

export type EvaluationStage = {
  name: string;
  status: StageStatus;
  message?: string | null;
  event_uuid?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
};

export type EvidenceCandidate = {
  uuid: string;
  claim_uuid: string;
  evidence_uuid: string;
  source_kind: EvidenceSourceKind;
  title: string;
  raw_text: string;
  excerpt?: string | null;
  source_url: string;
  paper_uuid?: string | null;
  source_uuid?: string | null;
  candidate_uuid?: string | null;
  chunk_id?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  section?: string | null;
  publication_status?: string | null;
  is_preprint: boolean;
  source_policy_notes: string[];
  selection_status?: string | null;
  used_as_citation: boolean;
  metadata: Record<string, unknown>;
};

export type EvidenceCitation = {
  uuid: string;
  claim_uuid: string;
  evidence_uuid: string;
  source_kind: EvidenceSourceKind;
  title: string;
  source_url: string;
  paper_uuid?: string | null;
  source_uuid?: string | null;
  candidate_uuid?: string | null;
  chunk_id?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  section?: string | null;
  excerpt: string;
  publication_status?: string | null;
  is_preprint: boolean;
  source_policy_notes: string[];
};

export type SubclaimEvaluation = {
  uuid: string;
  text: string;
  label: EvaluationLabel;
  rationale: string;
  citation_uuids: string[];
  uncertainty_note?: string | null;
  overclaim_note?: string | null;
};

export type ClaimEvaluation = {
  uuid: string;
  claim_uuid: string;
  claim_text: string;
  label: EvaluationLabel;
  rationale: string;
  citations: EvidenceCitation[];
  candidate_evidence: EvidenceCandidate[];
  unused_candidate_evidence: EvidenceCandidate[];
  subclaims: SubclaimEvaluation[];
  uncertainty_note?: string | null;
  overclaim_note?: string | null;
  source_limit_notes: string[];
  preprint_notes: string[];
  news_exception: boolean;
  transcript_excerpt?: string | null;
  screenshot_uuids: string[];
  created_at: string;
};

export type EvaluationValidationError = {
  uuid: string;
  claim_uuid?: string | null;
  evidence_uuid?: string | null;
  code: string;
  message: string;
};

export type ReportVersion = {
  report_uuid: string;
  report_group_uuid: string;
  version: number;
  markdown_path: string;
  ingestion_job_uuid: string;
  ground_truth_job_uuid: string;
  source_video_uuid?: string | null;
  claim_uuids: string[];
  cited_evidence_uuids: string[];
  candidate_evidence_uuids: string[];
  label_counts: Partial<Record<EvaluationLabel, number>>;
  narrative_markdown: string;
  source_policy_notes: string[];
  evaluations: ClaimEvaluation[];
  cited_evidence: EvidenceCitation[];
  unused_candidate_evidence: EvidenceCandidate[];
  validation_errors: EvaluationValidationError[];
  rerun_available: boolean;
  created_at: string;
  updated_at: string;
};

export type EvaluationJob = {
  job_uuid: string;
  ingestion_job_uuid: string;
  ground_truth_job_uuid: string;
  status: JobLifecycleStatus;
  current_operation: string;
  stages: EvaluationStage[];
  report?: ReportVersion | null;
  report_versions: ReportVersion[];
  validation_errors: EvaluationValidationError[];
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

export async function startReportJobFromGroundTruth(
  groundTruthJobUuid: string,
): Promise<EvaluationJob> {
  return parseResponse<EvaluationJob>(
    await fetch(`${API_BASE_URL}/reports/jobs/from-ground-truth/${groundTruthJobUuid}`, {
      method: "POST",
    }),
    "report_request_failed",
  );
}

export async function rerunReportJobFromGroundTruth(
  groundTruthJobUuid: string,
): Promise<EvaluationJob> {
  return parseResponse<EvaluationJob>(
    await fetch(`${API_BASE_URL}/reports/jobs/from-ground-truth/${groundTruthJobUuid}/rerun`, {
      method: "POST",
    }),
    "report_rerun_failed",
  );
}

export async function fetchReportJob(jobUuid: string): Promise<EvaluationJob> {
  return parseResponse<EvaluationJob>(
    await fetch(`${API_BASE_URL}/reports/jobs/${jobUuid}`),
    "report_job_fetch_failed",
  );
}

export async function fetchReport(reportUuid: string): Promise<ReportVersion> {
  return parseResponse<ReportVersion>(
    await fetch(`${API_BASE_URL}/reports/${reportUuid}`),
    "report_fetch_failed",
  );
}
