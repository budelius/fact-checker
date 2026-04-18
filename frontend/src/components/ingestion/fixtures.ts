import type { IngestionJob } from "../../api/ingestion";

const now = "2026-04-18T12:00:00Z";

export const emptyIngestionJobFixture: IngestionJob = {
  job_uuid: "00000000-0000-4000-8000-000000000100",
  source_kind: "fixture_transcript",
  source_url: "https://www.tiktok.com/@fixture/video/1234567890",
  status: "pending",
  current_operation: "Waiting to start ingestion.",
  stages: [],
  artifacts: [],
  created_at: now,
  updated_at: now,
};

export const runningIngestionJobFixture: IngestionJob = {
  ...emptyIngestionJobFixture,
  job_uuid: "00000000-0000-4000-8000-000000000101",
  status: "running",
  current_operation: "Building transcript",
  stages: [{ name: "build_transcript", status: "running", message: "Building transcript" }],
};

export const completeResearchBackedJobFixture: IngestionJob = {
  ...emptyIngestionJobFixture,
  job_uuid: "00000000-0000-4000-8000-000000000102",
  status: "succeeded",
  current_operation: "Source candidates ready for paper discovery.",
  transcript_artifact: {
    transcript_uuid: "00000000-0000-4000-8000-000000000201",
    video_uuid: "00000000-0000-4000-8000-000000000202",
    provenance: {
      method: "fixture",
      source_url: "https://www.tiktok.com/@fixture/video/1234567890",
    },
    segments: [
      {
        uuid: "00000000-0000-4000-8000-000000000203",
        start_seconds: 1,
        end_seconds: 3.5,
        text: "A paper says transformers scale well for sequence modeling.",
      },
    ],
    plain_text: "A paper says transformers scale well for sequence modeling. arXiv:1706.03762",
  },
  claims: [
    {
      uuid: "00000000-0000-4000-8000-000000000301",
      source_video_uuid: "00000000-0000-4000-8000-000000000202",
      source_transcript_uuid: "00000000-0000-4000-8000-000000000201",
      timestamp_start_seconds: 1,
      timestamp_end_seconds: 3.5,
      transcript_excerpt: "transformers scale well",
      claim_text: "Transformers scale well for sequence modeling.",
      screenshot_uuids: [],
      extraction_confidence: 0.68,
      evidence_status: "pending",
      source_candidate_count: 1,
    },
    {
      uuid: "00000000-0000-4000-8000-000000000302",
      source_video_uuid: "00000000-0000-4000-8000-000000000202",
      source_transcript_uuid: "00000000-0000-4000-8000-000000000201",
      transcript_excerpt: "arXiv:1706.03762",
      claim_text: "The video references arXiv:1706.03762.",
      screenshot_uuids: [],
      extraction_confidence: 0.72,
      evidence_status: "pending",
      source_candidate_count: 1,
    },
  ],
  research_basis: {
    status: "source_candidates_found",
    reason: "Source candidates found in transcript context.",
    candidate_count: 1,
    candidates: [
      {
        uuid: "00000000-0000-4000-8000-000000000401",
        candidate_type: "arXiv",
        value: "1706.03762",
        source: "transcript",
      },
    ],
  },
};

export const uploadedVideoJobFixture: IngestionJob = {
  ...completeResearchBackedJobFixture,
  job_uuid: "00000000-0000-4000-8000-000000000103",
  source_kind: "uploaded_video",
  source_url: "uploaded://fixture.mp4",
  artifacts: [
    {
      artifact_type: "media_retrieval",
      status: "succeeded",
      label: "Media retrieval",
      message: "Uploaded video stored locally.",
      details: {
        vault_path: "vault/raw/videos/fixture-00000000.mp4",
        third_party_upload: false,
      },
    },
  ],
};

export const opinionUnratableJobFixture: IngestionJob = {
  ...emptyIngestionJobFixture,
  job_uuid: "00000000-0000-4000-8000-000000000104",
  status: "succeeded",
  current_operation: "No paper or source references found.",
  research_basis: {
    status: "opinion_or_unratable",
    reason: "No paper or source references found in transcript or screenshots.",
    candidate_count: 0,
    candidates: [],
  },
};
