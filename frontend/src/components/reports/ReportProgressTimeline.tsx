import type { EvaluationStage } from "../../api/reports";

const stageLabels: Record<string, string> = {
  load_claims: "Load claims",
  load_evidence: "Load evidence",
  select_citations: "Select citations",
  evaluate_claims: "Evaluate claims",
  validate_citations: "Validate citations",
  write_report: "Write report",
  index_and_link: "Index and link",
};

export function ReportProgressTimeline({ stages }: { stages: EvaluationStage[] }) {
  if (!stages.length) {
    return null;
  }

  return (
    <section className="ingestion-panel report-section">
      <h2>Report progress</h2>
      <ol className="timeline-list" aria-live="polite">
        {stages.map((stage) => (
          <li className={`timeline-row timeline-row--${stage.status}`} key={stage.name}>
            <span className="timeline-row__dot" aria-hidden="true" />
            <div>
              <div className="timeline-row__title">{stageLabels[stage.name] ?? stage.name}</div>
              <div className="timeline-row__message">{stage.message || stage.status}</div>
            </div>
            <span className="status-pill">
              {stage.status === "succeeded" ? "complete" : stage.status}
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}
