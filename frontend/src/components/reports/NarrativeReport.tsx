import type { ReportVersion } from "../../api/reports";

const labelOrder = ["supported", "contradicted", "mixed", "insufficient"] as const;

export function NarrativeReport({ report }: { report: ReportVersion }) {
  return (
    <section className="ingestion-panel report-narrative">
      <div className="report-narrative__header">
        <div>
          <span className="section-label">Fact-check report</span>
          <h2>Narrative report</h2>
        </div>
        <div className="label-count-grid" aria-label="Evaluation label counts">
          {labelOrder.map((label) => (
            <div className={`label-count label-count--${label}`} key={label}>
              <span>{label}</span>
              <strong>{report.label_counts[label] ?? 0}</strong>
            </div>
          ))}
        </div>
      </div>

      <p className="report-narrative__body">{report.narrative_markdown}</p>
    </section>
  );
}
