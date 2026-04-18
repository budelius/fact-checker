import type {
  KnowledgeConsistencySummary,
  KnowledgeGraphResponse,
  KnowledgeNoteDetail,
  KnowledgeRatingSummary,
} from "../api/knowledge";
import { ConsistencyPanel } from "./ConsistencyPanel";
import { KnowledgeGraphPanel } from "./KnowledgeGraphPanel";
import { RatingBadge } from "./RatingBadge";

type NotePreviewProps = {
  note: KnowledgeNoteDetail | null;
  graph?: KnowledgeGraphResponse | null;
  consistency?: KnowledgeConsistencySummary | null;
  rating?: KnowledgeRatingSummary | null;
  onCheckConsistency?: () => void;
};

function renderMarkdown(markdown: string) {
  return markdown.split(/\n{2,}/).map((block) => {
    const trimmed = block.trim();
    if (!trimmed) {
      return null;
    }
    if (trimmed.startsWith("#")) {
      const level = Math.min(trimmed.match(/^#+/)?.[0].length ?? 2, 3);
      const text = trimmed.replace(/^#+\s*/, "");
      const Heading = `h${level}` as "h1" | "h2" | "h3";
      return <Heading key={trimmed}>{text}</Heading>;
    }
    if (trimmed.startsWith("- ")) {
      return (
        <ul key={trimmed}>
          {trimmed.split("\n").map((line) => (
            <li key={line}>{line.replace(/^-\s*/, "")}</li>
          ))}
        </ul>
      );
    }
    return <p key={trimmed}>{trimmed}</p>;
  });
}

export function NotePreview({
  note,
  graph,
  consistency,
  rating,
  onCheckConsistency,
}: NotePreviewProps) {
  if (!note) {
    return (
      <article className="note-preview note-preview--empty">
        <h1>No note selected</h1>
        <p>Choose a vault page or search the brain to inspect stored evidence.</p>
      </article>
    );
  }

  return (
    <article className="note-preview">
      <div className="note-preview__meta">
        <span>{note.entity_type}</span>
        <span>{note.updated_at ?? "unknown update time"}</span>
        <span>{note.vault_path}</span>
      </div>
      <div className="note-preview__title-row">
        <div>
          <h1>{note.title}</h1>
          <p className="note-preview__type">{note.uuid}</p>
        </div>
        <RatingBadge rating={rating ?? note.rating} />
      </div>

      <section className="note-preview__body" aria-label="Generated Markdown body">
        {renderMarkdown(note.body_markdown)}
      </section>

      <section className="note-preview__section">
        <h2>Backlinks</h2>
        {note.backlinks.length ? (
          <div className="relationship-list">
            {note.backlinks.map((backlink) => (
              <div className="relationship-row" key={backlink.uuid}>
                <span className="relationship-row__type">{backlink.relationship_type ?? "links"}</span>
                <span className="relationship-row__target">{backlink.title}</span>
                <span className="relationship-row__entity">{backlink.entity_type}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">No relationships recorded yet</p>
        )}
      </section>

      <KnowledgeGraphPanel graph={graph} />
      <ConsistencyPanel consistency={consistency ?? note.consistency} onCheckConsistency={onCheckConsistency} />

      <details className="frontmatter-details">
        <summary>Frontmatter</summary>
        <pre className="frontmatter" aria-label="Frontmatter preview">
          {JSON.stringify(note.frontmatter, null, 2)}
        </pre>
      </details>
    </article>
  );
}
