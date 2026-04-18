import type { KnowledgeConsistencySummary } from "../api/knowledge";

type ConsistencyPanelProps = {
  consistency?: KnowledgeConsistencySummary | null;
  onCheckConsistency?: () => void;
};

export function ConsistencyPanel({ consistency, onCheckConsistency }: ConsistencyPanelProps) {
  const statusOptions = "synced drift broken";

  return (
    <section className="consistency-panel">
      <div className="panel-heading">
        <h2>Consistency</h2>
        <button className="secondary-action" onClick={onCheckConsistency} type="button">
          Check consistency
        </button>
      </div>

      {consistency ? (
        <>
          <div
            className={`consistency-status consistency-status--${consistency.status}`}
            data-status-options={statusOptions}
          >
            {consistency.status === "synced"
              ? "Markdown, MongoDB, and Qdrant are in sync."
              : consistency.status}
          </div>
          <div className="consistency-grid">
            <span>notes {consistency.checked_notes}</span>
            <span>mongo {consistency.missing_mongo_records}</span>
            <span>qdrant {consistency.missing_qdrant_payloads}</span>
            <span>broken {consistency.broken_relationships}</span>
            <span>orphan {consistency.orphan_vectors}</span>
          </div>
          <div className="consistency-list">
            {consistency.issues.map((issue) => (
              <div className={`consistency-row consistency-row--${issue.status}`} key={issue.issue}>
                <span>{issue.status}</span>
                <strong>{issue.store}</strong>
                <p>{issue.issue}</p>
                <small>{issue.suggested_repair}</small>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="empty-state">This knowledge view could not load. Keep the UUID and retry after checking the backend logs.</p>
      )}
    </section>
  );
}
