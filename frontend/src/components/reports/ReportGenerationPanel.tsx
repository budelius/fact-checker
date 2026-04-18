import { FileCheck2, RefreshCw } from "lucide-react";

import type { GroundTruthJob } from "../../api/groundTruth";
import type { IngestionJob } from "../../api/ingestion";
import type { EvaluationJob, ReportVersion } from "../../api/reports";
import { ClaimEvaluationList } from "./ClaimEvaluationList";
import { NarrativeReport } from "./NarrativeReport";
import { ReportProgressTimeline } from "./ReportProgressTimeline";
import { ReportStatusHeader } from "./ReportStatusHeader";
import { ReportVersionList } from "./ReportVersionList";

type ReportGenerationPanelProps = {
  ingestionJob?: IngestionJob | null;
  groundTruthJob?: GroundTruthJob | null;
  reportJob?: EvaluationJob | null;
  report?: ReportVersion | null;
  error?: string | null;
  isGenerating: boolean;
  isRerunning: boolean;
  onGenerate: () => void;
  onRerun: () => void;
};

export function ReportGenerationPanel({
  ingestionJob,
  groundTruthJob,
  reportJob,
  report,
  error,
  isGenerating,
  isRerunning,
  onGenerate,
  onRerun,
}: ReportGenerationPanelProps) {
  const hasClaims = Boolean(ingestionJob?.claims?.length);
  const canGenerate = hasClaims && !isGenerating && !isRerunning;
  const canRerun = Boolean(report) && !isGenerating && !isRerunning;
  const selectedEvidenceCount = groundTruthJob?.chunks.length ?? 0;

  return (
    <div className="report-workspace" aria-label="Fact-check report workspace">
      <section className="ingestion-panel report-generation-panel">
        <div className="report-panel__header">
          <div>
            <h2>Fact-check report</h2>
            <p className="panel-summary">
              {report
                ? `Report v${report.version} is stored at ${report.markdown_path}.`
                : hasClaims
                  ? "Claims are ready for evidence evaluation."
                  : "Extract claims before starting evidence evaluation."}
            </p>
          </div>
          <div className="report-actions">
            <button
              className="primary-action"
              disabled={!canGenerate}
              onClick={onGenerate}
              type="button"
            >
              <FileCheck2 aria-hidden="true" size={18} />
              {isGenerating ? "Generating" : "Generate report"}
            </button>
            <button
              className="secondary-action"
              disabled={!canRerun}
              onClick={onRerun}
              type="button"
            >
              <RefreshCw aria-hidden="true" size={18} />
              {isRerunning ? "Rerunning" : "Rerun report"}
            </button>
          </div>
        </div>

        <dl className="report-readiness">
          <div>
            <dt>claims</dt>
            <dd>{ingestionJob?.claims?.length ?? 0}</dd>
          </div>
          <div>
            <dt>ground_truth_job</dt>
            <dd>{groundTruthJob?.job_uuid ?? "not started"}</dd>
          </div>
          <div>
            <dt>selected_evidence_chunks</dt>
            <dd>{selectedEvidenceCount}</dd>
          </div>
        </dl>

        {error ? <div className="recoverable-error">{error}</div> : null}
      </section>

      <ReportStatusHeader job={reportJob} report={report} />
      <ReportProgressTimeline stages={reportJob?.stages ?? []} />

      {report ? (
        <>
          <NarrativeReport report={report} />
          <ClaimEvaluationList evaluations={report.evaluations} />
          <ReportVersionList
            activeReportUuid={report.report_uuid}
            versions={reportJob?.report_versions ?? [report]}
          />
        </>
      ) : null}
    </div>
  );
}
