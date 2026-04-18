export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type JobLifecycleStatus = "pending" | "running" | "succeeded" | "failed";
export type StageStatus = "pending" | "running" | "succeeded" | "failed" | "skipped";
export type ArtifactType =
  | "public_metadata"
  | "transcript"
  | "media_retrieval"
  | "screenshot"
  | "claims"
  | "research_basis";
export type ResearchBasisStatus =
  | "source_candidates_found"
  | "no_research_source_found"
  | "opinion_or_unratable"
  | "needs_manual_review";

export type IngestionStage = {
  name: string;
  status: StageStatus;
  message: string;
  entity_uuid?: string | null;
};

export type ArtifactStatus = {
  artifact_type: ArtifactType;
  status: StageStatus;
  label: string;
  entity_uuid?: string | null;
  message: string;
  details: Record<string, unknown>;
};

export type TranscriptSegment = {
  uuid: string;
  start_seconds?: number | null;
  end_seconds?: number | null;
  text: string;
};

export type TranscriptArtifact = {
  transcript_uuid: string;
  video_uuid: string;
  provenance: {
    method: string;
    source_url: string;
    provider?: string | null;
    quality_note?: string | null;
    failure_reason?: string | null;
  };
  segments: TranscriptSegment[];
  plain_text: string;
  vault_path?: string | null;
};

export type ScreenshotArtifact = {
  screenshot_uuid: string;
  video_uuid: string;
  timestamp_seconds?: number | null;
  vault_path: string;
  asset_url?: string | null;
  source_clue: boolean;
  source_clue_text?: string | null;
  claim_uuids: string[];
};

export type ExtractedClaim = {
  uuid: string;
  source_video_uuid: string;
  source_transcript_uuid: string;
  timestamp_start_seconds?: number | null;
  timestamp_end_seconds?: number | null;
  transcript_excerpt: string;
  claim_text: string;
  screenshot_uuids: string[];
  extraction_confidence?: number | null;
  evidence_status: "pending";
  source_candidate_count: number;
};

export type ResearchBasisCandidate = {
  uuid: string;
  candidate_type: string;
  value: string;
  source: string;
  source_uuid?: string | null;
  confidence?: number | null;
};

export type ResearchBasisTriage = {
  status: ResearchBasisStatus;
  candidates: ResearchBasisCandidate[];
  reason: string;
  candidate_count: number;
};

export type IngestionJob = {
  job_uuid: string;
  source_kind: string;
  source_url: string;
  status: JobLifecycleStatus;
  current_operation: string;
  stages: IngestionStage[];
  artifacts: ArtifactStatus[];
  created_at: string;
  updated_at: string;
  error_message?: string | null;
  video_uuid?: string | null;
  public_metadata?: Record<string, unknown>;
  transcript_artifact?: TranscriptArtifact | null;
  screenshots?: ScreenshotArtifact[];
  claims?: ExtractedClaim[];
  research_basis?: ResearchBasisTriage;
};

export function displayLifecycleStatus(status: JobLifecycleStatus) {
  return status === "succeeded" ? "complete" : status;
}

async function parseResponse(response: Response): Promise<IngestionJob> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(typeof payload.detail === "string" ? payload.detail : "ingestion_request_failed");
  }

  return response.json() as Promise<IngestionJob>;
}

export async function submitTikTokUrl(url: string): Promise<IngestionJob> {
  return parseResponse(
    await fetch(`${API_BASE_URL}/ingestion/tiktok`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }),
  );
}

export async function submitPastedTranscript(
  sourceUrl: string,
  transcript: string,
): Promise<IngestionJob> {
  return parseResponse(
    await fetch(`${API_BASE_URL}/ingestion/fixtures/transcript`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_url: sourceUrl, transcript }),
    }),
  );
}

export async function uploadVideoFile(file: File, transcript?: string): Promise<IngestionJob> {
  const form = new FormData();
  form.append("file", file);
  if (transcript) {
    form.append("transcript", transcript);
  }

  return parseResponse(
    await fetch(`${API_BASE_URL}/ingestion/videos/upload`, {
      method: "POST",
      body: form,
    }),
  );
}

export async function fetchIngestionJob(jobUuid: string): Promise<IngestionJob> {
  return parseResponse(await fetch(`${API_BASE_URL}/ingestion/jobs/${jobUuid}`));
}

export function resolveApiAssetUrl(assetUrl?: string | null): string | null {
  if (!assetUrl) {
    return null;
  }

  if (/^https?:\/\//i.test(assetUrl) || assetUrl.startsWith("data:")) {
    return assetUrl;
  }

  return `${API_BASE_URL}${assetUrl.startsWith("/") ? "" : "/"}${assetUrl}`;
}
