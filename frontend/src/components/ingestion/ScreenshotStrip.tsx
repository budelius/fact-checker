import type { ScreenshotArtifact } from "../../api/ingestion";

function formatTime(value?: number | null) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}s`;
}

export function ScreenshotStrip({ screenshots }: { screenshots: ScreenshotArtifact[] }) {
  return (
    <section className="screenshot-strip">
      {screenshots.length ? (
        screenshots.map((screenshot) => (
          <div className="screenshot-thumb" key={screenshot.screenshot_uuid}>
            <span>{formatTime(screenshot.timestamp_seconds)}</span>
            <strong>{screenshot.source_clue ? "source clue" : "frame"}</strong>
            <small>{screenshot.vault_path}</small>
          </div>
        ))
      ) : (
        <p className="empty-state">No source-clue frames captured yet.</p>
      )}
    </section>
  );
}
