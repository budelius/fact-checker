import type { FormEvent } from "react";
import { useState } from "react";

import { submitPastedTranscript, submitTikTokUrl, uploadVideoFile, type IngestionJob } from "../api/ingestion";
import { ArtifactStatusGrid } from "./ingestion/ArtifactStatusGrid";
import { ClaimExtractionList } from "./ingestion/ClaimExtractionList";
import { JobStatusHeader } from "./ingestion/JobStatusHeader";
import { ProgressTimeline } from "./ingestion/ProgressTimeline";
import { RecoverableError } from "./ingestion/RecoverableError";
import { ResearchBasisPanel } from "./ingestion/ResearchBasisPanel";
import { ScreenshotStrip } from "./ingestion/ScreenshotStrip";
import { TikTokSubmissionPanel } from "./ingestion/TikTokSubmissionPanel";
import { TranscriptPreview } from "./ingestion/TranscriptPreview";

const sampleTranscript =
  "00:00:01.000 --> 00:00:03.500\n" +
  "A paper says transformers scale well for sequence modeling.\n\n" +
  "00:00:04.000 --> 00:00:06.000\n" +
  "The source is arXiv:1706.03762.";

export function IngestionWorkbench() {
  const [url, setUrl] = useState("https://www.tiktok.com/@fixture/video/1234567890");
  const [transcript, setTranscript] = useState(sampleTranscript);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const nextJob = transcript.trim()
        ? await submitPastedTranscript(url, transcript)
        : await submitTikTokUrl(url);
      setJob(nextJob);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "ingestion_request_failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function submitUpload() {
    if (!selectedFile) {
      setError("Select a video file before uploading.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      setJob(await uploadVideoFile(selectedFile, transcript));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "ingestion_request_failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="ingestion-workspace">
      <TikTokSubmissionPanel
        isSubmitting={isSubmitting}
        onFileChange={setSelectedFile}
        onSubmitUpload={submitUpload}
        onSubmitUrl={submitUrl}
        onTranscriptChange={setTranscript}
        onUrlChange={setUrl}
        onUseSampleTranscript={() => setTranscript(sampleTranscript)}
        selectedFile={selectedFile}
        transcript={transcript}
        url={url}
      />

      {error ? <RecoverableError error={error} /> : null}

      {job ? (
        <>
          <JobStatusHeader job={job} />
          <ProgressTimeline stages={job.stages} />
          <ArtifactStatusGrid artifacts={job.artifacts} />
          <TranscriptPreview segments={job.transcript_artifact?.segments ?? []} />
          <ClaimExtractionList claims={job.claims ?? []} />
          <ResearchBasisPanel researchBasis={job.research_basis} />
          <ScreenshotStrip screenshots={job.screenshots ?? []} />
        </>
      ) : (
        <section className="ingestion-panel">
          <h2>Job status</h2>
          <p className="empty-state">
            Submit the sample transcript or upload a video to create a local Phase 2 job without
            live TikTok or OpenAI access.
          </p>
        </section>
      )}
    </div>
  );
}
