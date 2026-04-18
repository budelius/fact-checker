import { ImageIcon } from "lucide-react";
import { useState } from "react";

import { resolveApiAssetUrl, type ScreenshotArtifact } from "../../api/ingestion";

function formatTime(value?: number | null) {
  if (value === null || value === undefined) {
    return "--";
  }
  return `${value.toFixed(1)}s`;
}

function ScreenshotPreview({
  assetUrl,
  label,
}: {
  assetUrl?: string | null;
  label: string;
}) {
  const [failed, setFailed] = useState(false);
  const resolvedUrl = resolveApiAssetUrl(assetUrl);

  if (!resolvedUrl || failed) {
    return (
      <div className="screenshot-placeholder">
        <ImageIcon aria-hidden="true" size={22} />
        <span>Preview unavailable</span>
      </div>
    );
  }

  return (
    <img
      alt={label}
      className="screenshot-image"
      loading="lazy"
      onError={() => setFailed(true)}
      src={resolvedUrl}
    />
  );
}

export function ScreenshotStrip({ screenshots }: { screenshots: ScreenshotArtifact[] }) {
  return (
    <section className="ingestion-panel">
      <h2>Screenshots/keyframes</h2>
      {screenshots.length ? (
        <div className="screenshot-strip">
          {screenshots.map((screenshot) => {
            const label = screenshot.source_clue ? "Source clue preview" : "Video frame preview";
            return (
              <article className="screenshot-thumb" key={screenshot.screenshot_uuid}>
                <div className="screenshot-thumb__media">
                  <ScreenshotPreview assetUrl={screenshot.asset_url} label={label} />
                  <span className="screenshot-badge">
                    {screenshot.source_clue ? "source clue" : "frame"}
                  </span>
                </div>
                <div className="screenshot-thumb__meta">
                  <span>{formatTime(screenshot.timestamp_seconds)}</span>
                  <small>{screenshot.screenshot_uuid}</small>
                  <small>{screenshot.vault_path}</small>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <p className="empty-state">No source-clue frames captured yet.</p>
      )}
    </section>
  );
}
