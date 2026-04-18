import type { ReportVersion } from "../../api/reports";

const labelOrder = ["supported", "contradicted", "mixed", "insufficient"] as const;

export function ReportProvenancePanel({ report }: { report: ReportVersion }) {
  return (
    <section className="metadata-panel report-provenance-panel">
      <h2>Report provenance</h2>
      <dl className="metadata-list">
        <div>
          <dt>report_uuid</dt>
          <dd>{report.report_uuid}</dd>
        </div>
        <div>
          <dt>report_group_uuid</dt>
          <dd>{report.report_group_uuid}</dd>
        </div>
        <div>
          <dt>version</dt>
          <dd>{report.version}</dd>
        </div>
        <div>
          <dt>markdown_path</dt>
          <dd>{report.markdown_path}</dd>
        </div>
        <div>
          <dt>ground_truth_job_uuid</dt>
          <dd>{report.ground_truth_job_uuid}</dd>
        </div>
      </dl>

      <h2>labels</h2>
      <div className="provenance-label-list">
        {labelOrder.map((label) => (
          <div className={`label-count label-count--${label}`} key={label}>
            <span>{label}</span>
            <strong>{report.label_counts[label] ?? 0}</strong>
          </div>
        ))}
      </div>

      <h2>source policy</h2>
      <div className="policy-note-list">
        <span className="policy-note">Paper summaries are navigation only</span>
        {report.source_policy_notes.map((note) => (
          <span className="policy-note" key={note}>
            {note}
          </span>
        ))}
      </div>

      <h2>evidence</h2>
      <dl className="metadata-list">
        <div>
          <dt>cited_evidence</dt>
          <dd>{report.cited_evidence_uuids.length}</dd>
        </div>
        <div>
          <dt>candidate_evidence</dt>
          <dd>{report.candidate_evidence_uuids.length}</dd>
        </div>
        <div>
          <dt>claims</dt>
          <dd>{report.claim_uuids.length}</dd>
        </div>
        <div>
          <dt>validation_errors</dt>
          <dd>{report.validation_errors.length}</dd>
        </div>
      </dl>
    </section>
  );
}
