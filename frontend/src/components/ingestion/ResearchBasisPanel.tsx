import type { ResearchBasisTriage } from "../../api/ingestion";

function statusCopy(status: ResearchBasisTriage["status"]) {
  if (status === "source_candidates_found") {
    return "Source candidates found";
  }
  if (status === "needs_manual_review") {
    return "Needs manual review";
  }
  if (status === "opinion_or_unratable") {
    return "Opinion-based for now";
  }
  return "No research source found";
}

export function ResearchBasisPanel({ researchBasis }: { researchBasis?: ResearchBasisTriage }) {
  return (
    <section className="ingestion-panel">
      <h2>Research basis</h2>
      {researchBasis ? (
        <div className="research-basis">
          <strong>{statusCopy(researchBasis.status)}</strong>
          <p>{researchBasis.reason}</p>
          <div className="candidate-list">
            {researchBasis.candidates.map((candidate) => (
              <span className="candidate-chip" key={candidate.uuid}>
                {candidate.candidate_type}: {candidate.value}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <p className="empty-state">
          No paper or source references found in transcript or screenshots. Marked opinion-based for
          now.
        </p>
      )}
    </section>
  );
}
