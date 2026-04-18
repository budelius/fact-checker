import type { TranscriptSegment } from "../../api/ingestion";

function formatTime(value?: number | null) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}s`;
}

export function TranscriptPreview({ segments }: { segments: TranscriptSegment[] }) {
  if (segments.length === 0) {
    return (
      <section className="ingestion-panel">
        <h2>Transcript</h2>
        <p className="empty-state">Transcript unavailable</p>
      </section>
    );
  }

  return (
    <section className="ingestion-panel">
      <h2>Transcript</h2>
      <div className="transcript-list">
        {segments.map((segment) => (
          <div className="transcript-row" key={segment.uuid}>
            <span className="transcript-row__time">
              {formatTime(segment.start_seconds)}-{formatTime(segment.end_seconds)}
            </span>
            <span>{segment.text}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
