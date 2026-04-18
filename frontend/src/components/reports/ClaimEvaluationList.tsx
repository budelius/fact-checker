import type { ClaimEvaluation } from "../../api/reports";
import { ClaimEvaluationRow } from "./ClaimEvaluationRow";

export function ClaimEvaluationList({ evaluations }: { evaluations: ClaimEvaluation[] }) {
  return (
    <section className="ingestion-panel report-section">
      <h2>Claims checked</h2>
      {evaluations.length ? (
        <div className="claim-evaluation-list">
          {evaluations.map((evaluation) => (
            <ClaimEvaluationRow evaluation={evaluation} key={evaluation.uuid} />
          ))}
        </div>
      ) : (
        <p className="empty-state">No claim evaluations recorded.</p>
      )}
    </section>
  );
}
