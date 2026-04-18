import { Sparkles } from "lucide-react";
import type { FormEvent } from "react";

type TikTokSubmissionPanelProps = {
  url: string;
  isSubmitting: boolean;
  onUrlChange: (value: string) => void;
  onSubmitUrl: (event: FormEvent<HTMLFormElement>) => void;
};

export function TikTokSubmissionPanel({
  url,
  isSubmitting,
  onUrlChange,
  onSubmitUrl,
}: TikTokSubmissionPanelProps) {
  return (
    <section className="submission-panel" aria-label="TikTok ingestion submission">
      <div>
        <h1>TikTok ingestion</h1>
        <p>Paste a public TikTok URL and let the pipeline extract the useful research context.</p>
      </div>

      <form className="submission-form" onSubmit={onSubmitUrl}>
        <label>
          <span>Public TikTok URL</span>
          <input value={url} onChange={(event) => onUrlChange(event.target.value)} type="url" />
        </label>

        <div className="submission-actions">
          <button className="primary-action" disabled={isSubmitting} type="submit">
            <Sparkles aria-hidden="true" size={18} />
            Check video
          </button>
        </div>
      </form>
    </section>
  );
}
