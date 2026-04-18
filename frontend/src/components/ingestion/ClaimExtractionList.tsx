import type { ExtractedClaim } from "../../api/ingestion";

function formatTime(value?: number | null) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}s`;
}

export function ClaimExtractionList({ claims }: { claims: ExtractedClaim[] }) {
  return (
    <section className="ingestion-panel">
      <h2>Extracted claims</h2>
      {claims.length ? (
        <div className="claim-list">
          {claims.map((claim) => (
            <article className="claim-row" key={claim.uuid}>
              <div className="claim-row__meta">
                <span>{claim.uuid}</span>
                <span>
                  {formatTime(claim.timestamp_start_seconds)}-{formatTime(claim.timestamp_end_seconds)}
                </span>
                <span>evidence_status: pending</span>
              </div>
              <strong>{claim.claim_text}</strong>
              <p>{claim.transcript_excerpt}</p>
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">No claims extracted yet.</p>
      )}
    </section>
  );
}
