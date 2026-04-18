import { ExternalLink } from "lucide-react";

import type { EvidenceCandidate, EvidenceCitation } from "../../api/reports";

type EvidenceLike = EvidenceCandidate | EvidenceCitation;

function evidenceExcerpt(evidence: EvidenceLike) {
  if ("raw_text" in evidence) {
    return evidence.excerpt || evidence.raw_text;
  }
  return evidence.excerpt;
}

function evidenceLocation(evidence: EvidenceLike) {
  const parts = [
    evidence.chunk_id ? `chunk ${evidence.chunk_id}` : null,
    evidence.section ? `section ${evidence.section}` : null,
    evidence.page_start !== null &&
    evidence.page_start !== undefined &&
    evidence.page_end !== null &&
    evidence.page_end !== undefined
      ? `pages ${evidence.page_start}-${evidence.page_end}`
      : null,
  ].filter(Boolean);

  return parts.join(" · ");
}

export function EvidenceSnippet({
  evidence,
  compact = false,
}: {
  evidence: EvidenceLike;
  compact?: boolean;
}) {
  const location = evidenceLocation(evidence);
  const excerpt = evidenceExcerpt(evidence);

  return (
    <article className={`evidence-snippet${compact ? " evidence-snippet--compact" : ""}`}>
      <div className="evidence-snippet__header">
        <div>
          <span className="section-label">{evidence.source_kind}</span>
          <strong>{evidence.title}</strong>
        </div>
        <a
          aria-label={`Open source for ${evidence.title}`}
          className="evidence-snippet__link"
          href={evidence.source_url}
          rel="noreferrer"
          target="_blank"
          title="Open source"
        >
          <ExternalLink aria-hidden="true" size={16} />
        </a>
      </div>

      <dl className="evidence-snippet__meta">
        <div>
          <dt>evidence_uuid</dt>
          <dd>{evidence.evidence_uuid}</dd>
        </div>
        {evidence.chunk_id ? (
          <div>
            <dt>chunk</dt>
            <dd>{evidence.chunk_id}</dd>
          </div>
        ) : null}
        {location ? (
          <div>
            <dt>location</dt>
            <dd>{location}</dd>
          </div>
        ) : null}
        {evidence.publication_status ? (
          <div>
            <dt>source_status</dt>
            <dd>{evidence.publication_status}</dd>
          </div>
        ) : null}
      </dl>

      {excerpt ? <p className="evidence-snippet__excerpt">{excerpt}</p> : null}

      {evidence.source_policy_notes.length ? (
        <div className="policy-note-list">
          {evidence.source_policy_notes.map((note) => (
            <span className="policy-note" key={note}>
              {note}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}
