import type { FormEvent } from "react";
import { useState } from "react";

import {
  startGroundTruthJobFromIngestion,
  type GroundTruthJob,
} from "../api/groundTruth";
import { submitTikTokUrl, type IngestionJob } from "../api/ingestion";
import {
  rerunReportJobFromGroundTruth,
  startReportJobFromGroundTruth,
  type EvaluationJob,
  type ReportVersion,
} from "../api/reports";
import { ArtifactStatusGrid } from "./ingestion/ArtifactStatusGrid";
import { ClaimExtractionList } from "./ingestion/ClaimExtractionList";
import { JobStatusHeader } from "./ingestion/JobStatusHeader";
import { ProgressTimeline } from "./ingestion/ProgressTimeline";
import { RecoverableError } from "./ingestion/RecoverableError";
import { ResearchBasisPanel } from "./ingestion/ResearchBasisPanel";
import { ScreenshotStrip } from "./ingestion/ScreenshotStrip";
import { TikTokSubmissionPanel } from "./ingestion/TikTokSubmissionPanel";
import { TranscriptPreview } from "./ingestion/TranscriptPreview";
import { ReportGenerationPanel } from "./reports/ReportGenerationPanel";

type IngestionWorkbenchProps = {
  onReportChange?: (report: ReportVersion | null) => void;
};

export function IngestionWorkbench({ onReportChange }: IngestionWorkbenchProps) {
  const [url, setUrl] = useState(
    "https://www.tiktok.com/@stephenlee96/video/7626043894639250702?_r=1&_t=ZN-95VcdJG75OA",
  );
  const [job, setJob] = useState<IngestionJob | null>(null);
  const [groundTruthJob, setGroundTruthJob] = useState<GroundTruthJob | null>(null);
  const [reportJob, setReportJob] = useState<EvaluationJob | null>(null);
  const [report, setReport] = useState<ReportVersion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isRerunningReport, setIsRerunningReport] = useState(false);

  function resetReportState() {
    setGroundTruthJob(null);
    setReportJob(null);
    setReport(null);
    setReportError(null);
    onReportChange?.(null);
  }

  function applyReportJob(nextReportJob: EvaluationJob) {
    const nextReport = nextReportJob.report ?? null;
    setReportJob(nextReportJob);
    setReport(nextReport);
    onReportChange?.(nextReport);

    if (nextReportJob.status === "failed") {
      setReportError(nextReportJob.error_message ?? "report_generation_failed");
      return;
    }

    if (!nextReport) {
      setReportError("report_generation_returned_no_report");
      return;
    }

    setReportError(null);
  }

  async function ensureGroundTruthJob() {
    if (!job) {
      throw new Error("ingestion_job_required");
    }

    if (groundTruthJob?.ingestion_job_uuid === job.job_uuid) {
      return groundTruthJob;
    }

    const nextGroundTruthJob = await startGroundTruthJobFromIngestion(job.job_uuid);
    setGroundTruthJob(nextGroundTruthJob);
    return nextGroundTruthJob;
  }

  async function submitUrl(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    resetReportState();
    try {
      setJob(await submitTikTokUrl(url));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "ingestion_request_failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function generateReport() {
    setIsGeneratingReport(true);
    setReportError(null);
    try {
      const nextGroundTruthJob = await ensureGroundTruthJob();
      if (nextGroundTruthJob.status === "failed") {
        setReportJob(null);
        setReport(null);
        onReportChange?.(null);
        throw new Error(nextGroundTruthJob.error_message ?? "ground_truth_discovery_failed");
      }
      applyReportJob(await startReportJobFromGroundTruth(nextGroundTruthJob.job_uuid));
    } catch (caught) {
      setReportError(caught instanceof Error ? caught.message : "report_generation_failed");
    } finally {
      setIsGeneratingReport(false);
    }
  }

  async function rerunReport() {
    const groundTruthJobUuid = groundTruthJob?.job_uuid ?? reportJob?.ground_truth_job_uuid;
    if (!groundTruthJobUuid) {
      setReportError("ground_truth_job_required");
      return;
    }

    setIsRerunningReport(true);
    setReportError(null);
    try {
      applyReportJob(await rerunReportJobFromGroundTruth(groundTruthJobUuid));
    } catch (caught) {
      setReportError(caught instanceof Error ? caught.message : "report_rerun_failed");
    } finally {
      setIsRerunningReport(false);
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
          <ReportGenerationPanel
            error={reportError}
            groundTruthJob={groundTruthJob}
            ingestionJob={job}
            isGenerating={isGeneratingReport}
            isRerunning={isRerunningReport}
            onGenerate={generateReport}
            onRerun={rerunReport}
            report={report}
            reportJob={reportJob}
          />
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
