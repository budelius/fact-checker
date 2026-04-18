import type { KnowledgeRatingSummary, RatingRecord } from "../api/knowledge";

type RatingBasisPanelProps = {
  rating?: KnowledgeRatingSummary | RatingRecord | null;
};

export function RatingBasisPanel({ rating }: RatingBasisPanelProps) {
  if (!rating) {
    return (
      <section className="rating-basis">
        <h2>Rating basis</h2>
        <p className="empty-state">insufficient history</p>
      </section>
    );
  }

  return (
    <section className="rating-basis">
      <h2>Rating basis</h2>
      <dl className="metadata-list">
        <div>
          <dt>Evidence count</dt>
          <dd>{rating.evidence_count}</dd>
        </div>
        <div>
          <dt>confidence_level</dt>
          <dd>{rating.confidence_level}</dd>
        </div>
        <div>
          <dt>source_basis</dt>
          <dd>{rating.source_basis.join(", ") || "None"}</dd>
        </div>
      </dl>
      <div className="label-distribution">
        {Object.entries(rating.label_distribution).map(([label, count]) => (
          <span className="label-count label-count--compact" key={label}>
            <span>{label}</span>
            <strong>{count}</strong>
          </span>
        ))}
      </div>
    </section>
  );
}
