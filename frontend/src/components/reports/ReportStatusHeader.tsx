import { Clipboard } from "lucide-react";

import { displayLifecycleStatus } from "../../api/ingestion";
import type { EvaluationJob, ReportVersion } from "../../api/reports";

export function ReportStatusHeader({
  job,
  report,
}: {
  job?: EvaluationJob | null;
  report?: ReportVersion | null;
}) {
  if (!job && !report) {
    return null;
  }

  const copyValue = report?.report_uuid ?? job?.job_uuid ?? "";

  return (
    <section className="job-header report-status-header" aria-live="polite">
      <div>
        <span className="section-label">Report UUID</span>
        <strong>{report?.report_uuid ?? "pending"}</strong>
      </div>
      <button
        aria-label="Copy report UUID"
        className="icon-button"
        disabled={!copyValue}
        onClick={() => navigator.clipboard.writeText(copyValue)}
        title="Copy report UUID"
        type="button"
      >
        <Clipboard aria-hidden="true" size={18} />
      </button>
      <div>
        <span className="section-label">Status</span>
        <strong>{job ? displayLifecycleStatus(job.status) : "stored"}</strong>
      </div>
      <div>
        <span className="section-label">Current operation</span>
        <strong>{job?.current_operation ?? `Report version ${report?.version ?? 1}`}</strong>
      </div>
    </section>
  );
}
