import { Clipboard } from "lucide-react";

import { displayLifecycleStatus, type IngestionJob } from "../../api/ingestion";

export function JobStatusHeader({ job }: { job: IngestionJob }) {
  return (
    <section className="job-header" aria-live="polite">
      <div>
        <span className="section-label">Job UUID</span>
        <strong>{job.job_uuid}</strong>
      </div>
      <button
        aria-label="Copy job UUID"
        className="icon-button"
        onClick={() => navigator.clipboard.writeText(job.job_uuid)}
        title="Copy job UUID"
        type="button"
      >
        <Clipboard aria-hidden="true" size={18} />
      </button>
      <div>
        <span className="section-label">Status</span>
        <strong>{displayLifecycleStatus(job.status)}</strong>
      </div>
      <div>
        <span className="section-label">Current operation</span>
        <strong>{job.current_operation}</strong>
      </div>
    </section>
  );
}
