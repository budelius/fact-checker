import type { TranscriptSegment } from "../../api/ingestion";

const PREVIEW_SEGMENT_LIMIT = 8;

function formatTime(value?: number | null) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}s`;
}

export function TranscriptPreview({ segments }: { segments: TranscriptSegment[] }) {
  const previewSegments = segments.slice(0, PREVIEW_SEGMENT_LIMIT);
  const hiddenSegmentCount = Math.max(0, segments.length - previewSegments.length);

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
      <p className="panel-summary">
        {segments.length} caption segments loaded
        {hiddenSegmentCount > 0 ? `, showing first ${previewSegments.length}` : ""}.
      </p>
      <div className="transcript-list">
        {previewSegments.map((segment) => (
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
