import type { EvidenceCitation } from "../../api/reports";
import { EvidenceSnippet } from "./EvidenceSnippet";

export function CitationList({ citations }: { citations: EvidenceCitation[] }) {
  if (!citations.length) {
    return <p className="empty-state">No citations recorded for this claim.</p>;
  }

  return (
    <div className="citation-list">
      {citations.map((citation) => (
        <EvidenceSnippet evidence={citation} key={citation.uuid} compact />
      ))}
    </div>
  );
}
