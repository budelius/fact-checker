import type { IngestionStage } from "../../api/ingestion";

const stageLabels: Record<string, string> = {
  validate_url: "Validate URL or upload",
  read_public_metadata: "Read public metadata",
  build_transcript: "Build transcript",
  capture_source_clues: "Capture source clues",
  extract_claims: "Extract claims",
  triage_research_basis: "Triage research basis",
  write_owned_artifacts: "Write owned artifacts",
};

export function ProgressTimeline({ stages }: { stages: IngestionStage[] }) {
  return (
    <section className="ingestion-panel">
      <h2>Progress</h2>
      <ol className="timeline-list" aria-live="polite">
        {stages.map((stage) => (
          <li className={`timeline-row timeline-row--${stage.status}`} key={stage.name}>
            <span className="timeline-row__dot" aria-hidden="true" />
            <div>
              <div className="timeline-row__title">{stageLabels[stage.name] ?? stage.name}</div>
              <div className="timeline-row__message">{stage.message || stage.status}</div>
            </div>
            <span className="status-pill">
              {stage.status === "succeeded" ? "complete" : stage.status}
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}
