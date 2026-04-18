import type { ClaimEvaluation, EvaluationLabel } from "../../api/reports";
import { CitationList } from "./CitationList";
import { EvidenceSnippet } from "./EvidenceSnippet";

const labelCopy: Record<EvaluationLabel, string> = {
  supported: "supported",
  contradicted: "contradicted",
  mixed: "mixed",
  insufficient: "insufficient",
};

export function ClaimEvaluationRow({ evaluation }: { evaluation: ClaimEvaluation }) {
  return (
    <article className={`claim-evaluation claim-evaluation--${evaluation.label}`}>
      <div className="claim-evaluation__header">
        <div className="claim-evaluation__title">
          <span className={`evaluation-label evaluation-label--${evaluation.label}`}>
            {labelCopy[evaluation.label]}
          </span>
          <strong>{evaluation.claim_text}</strong>
        </div>
        <span className="claim-evaluation__uuid">{evaluation.claim_uuid}</span>
      </div>

      <p className="claim-evaluation__rationale">{evaluation.rationale}</p>

      {evaluation.transcript_excerpt ? (
        <blockquote className="claim-evaluation__transcript">
          {evaluation.transcript_excerpt}
        </blockquote>
      ) : null}

      {evaluation.overclaim_note || evaluation.uncertainty_note ? (
        <div className="evaluation-note-grid">
          {evaluation.overclaim_note ? (
            <div>
              <span className="section-label">overclaim</span>
              <p>{evaluation.overclaim_note}</p>
            </div>
          ) : null}
          {evaluation.uncertainty_note ? (
            <div>
              <span className="section-label">uncertainty</span>
              <p>{evaluation.uncertainty_note}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      {evaluation.preprint_notes.length || evaluation.source_limit_notes.length ? (
        <div className="policy-note-list">
          {[...evaluation.preprint_notes, ...evaluation.source_limit_notes].map((note) => (
            <span className="policy-note" key={note}>
              {note}
            </span>
          ))}
        </div>
      ) : null}

      <div className="claim-evaluation__section">
        <h3>Citations</h3>
        <CitationList citations={evaluation.citations} />
      </div>

      {evaluation.unused_candidate_evidence.length ? (
        <div className="claim-evaluation__section">
          <h3>Candidate evidence reviewed</h3>
          <div className="citation-list">
            {evaluation.unused_candidate_evidence.map((candidate) => (
              <EvidenceSnippet evidence={candidate} key={candidate.uuid} compact />
            ))}
          </div>
        </div>
      ) : null}
    </article>
  );
}
