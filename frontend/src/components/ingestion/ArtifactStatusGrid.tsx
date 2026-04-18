import type { ArtifactStatus } from "../../api/ingestion";

function ArtifactCard({ artifact }: { artifact: ArtifactStatus }) {
  return (
    <div className="artifact-card">
      <div className="artifact-card__header">
        <span>{artifact.label}</span>
        <span className="status-pill">{artifact.status === "succeeded" ? "complete" : artifact.status}</span>
      </div>
      <p>{artifact.message}</p>
      {Object.keys(artifact.details).length > 0 ? (
        <dl className="artifact-card__details">
          {Object.entries(artifact.details).map(([key, value]) => (
            <div key={key}>
              <dt>{key}</dt>
              <dd>{String(value)}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </div>
  );
}

export function ArtifactStatusGrid({ artifacts }: { artifacts: ArtifactStatus[] }) {
  const fallback: ArtifactStatus[] = [
    {
      artifact_type: "screenshot",
      status: "pending",
      label: "Screenshots/keyframes",
      message: "No source-clue frames captured yet.",
      details: {},
    },
  ];

  return (
    <section className="artifact-grid">
      {(artifacts.length ? artifacts : fallback).map((artifact) => (
        <ArtifactCard
          artifact={artifact}
          key={`${artifact.artifact_type}-${artifact.label}-${artifact.status}`}
        />
      ))}
    </section>
  );
}
