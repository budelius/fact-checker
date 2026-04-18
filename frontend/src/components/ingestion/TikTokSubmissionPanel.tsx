import { FileText, RefreshCw, Upload } from "lucide-react";
import type { FormEvent } from "react";

type TikTokSubmissionPanelProps = {
  url: string;
  transcript: string;
  selectedFile: File | null;
  isSubmitting: boolean;
  onUrlChange: (value: string) => void;
  onTranscriptChange: (value: string) => void;
  onFileChange: (file: File | null) => void;
  onSubmitUrl: (event: FormEvent<HTMLFormElement>) => void;
  onSubmitUpload: () => void;
  onUseSampleTranscript: () => void;
  onReadMetadata: () => void;
};

export function TikTokSubmissionPanel({
  url,
  transcript,
  selectedFile,
  isSubmitting,
  onUrlChange,
  onTranscriptChange,
  onFileChange,
  onSubmitUrl,
  onSubmitUpload,
  onUseSampleTranscript,
  onReadMetadata,
}: TikTokSubmissionPanelProps) {
  return (
    <section className="submission-panel" aria-label="TikTok ingestion submission">
      <div>
        <h1>TikTok ingestion</h1>
        <p>Paste a public TikTok URL or upload a video</p>
      </div>

      <form className="submission-form" onSubmit={onSubmitUrl}>
        <label>
          <span>Public TikTok URL</span>
          <input value={url} onChange={(event) => onUrlChange(event.target.value)} type="url" />
        </label>

        <label>
          <span>Pasted transcript</span>
          <textarea
            rows={5}
            value={transcript}
            onChange={(event) => onTranscriptChange(event.target.value)}
          />
        </label>

        <div className="submission-actions">
          <button className="primary-action" disabled={isSubmitting} type="submit">
            <FileText aria-hidden="true" size={18} />
            Extract claims
          </button>
          <button
            className="secondary-action"
            disabled={isSubmitting}
            onClick={onReadMetadata}
            type="button"
          >
            <RefreshCw aria-hidden="true" size={18} />
            Read metadata
          </button>
          <button
            className="secondary-action"
            disabled={isSubmitting}
            onClick={onUseSampleTranscript}
            type="button"
          >
            <RefreshCw aria-hidden="true" size={18} />
            Use sample transcript
          </button>
        </div>
      </form>

      <div className="upload-row">
        <label>
          <span>Video file</span>
          <input
            accept=".mp4,.mov,.webm,video/mp4,video/quicktime,video/webm"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
            type="file"
          />
        </label>
        <button
          className="secondary-action"
          disabled={isSubmitting || !selectedFile}
          onClick={onSubmitUpload}
          type="button"
        >
          <Upload aria-hidden="true" size={18} />
          Upload video
        </button>
      </div>

      {selectedFile ? <p className="file-name">{selectedFile.name}</p> : null}
    </section>
  );
}
