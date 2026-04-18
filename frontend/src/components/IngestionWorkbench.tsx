import type { FormEvent } from "react";
import { useState } from "react";

import { submitTikTokUrl, type IngestionJob } from "../api/ingestion";
import { ArtifactStatusGrid } from "./ingestion/ArtifactStatusGrid";
import { ClaimExtractionList } from "./ingestion/ClaimExtractionList";
import { JobStatusHeader } from "./ingestion/JobStatusHeader";
import { ProgressTimeline } from "./ingestion/ProgressTimeline";
import { RecoverableError } from "./ingestion/RecoverableError";
import { ResearchBasisPanel } from "./ingestion/ResearchBasisPanel";
import { ScreenshotStrip } from "./ingestion/ScreenshotStrip";
import { TikTokSubmissionPanel } from "./ingestion/TikTokSubmissionPanel";
import { TranscriptPreview } from "./ingestion/TranscriptPreview";

export function IngestionWorkbench() {
  const [url, setUrl] = useState(
    "https://www.tiktok.com/@stephenlee96/video/7626043894639250702?_r=1&_t=ZN-95VcdJG75OA",
  );
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      setJob(await submitTikTokUrl(url));
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
        onSubmitUrl={submitUrl}
        onUrlChange={setUrl}
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
            Paste a public TikTok link and start the job. The app will read metadata, load captions,
            extract claims, and prepare source candidates when available.
          </p>
        </section>
      )}
    </div>
  );
}
