import { MessageSquarePlus } from "lucide-react";
import { useState } from "react";

import type {
  KnowledgeConsistencySummary,
  KnowledgeGraphResponse,
  KnowledgeNoteDetail,
  KnowledgeRatingSummary,
} from "../api/knowledge";
import { ConsistencyPanel } from "./ConsistencyPanel";
import { RatingBasisPanel } from "./RatingBasisPanel";

type MetadataPanelProps = {
  note: KnowledgeNoteDetail | null;
  graph?: KnowledgeGraphResponse | null;
  consistency?: KnowledgeConsistencySummary | null;
  rating?: KnowledgeRatingSummary | null;
  onAddAnnotation?: (body: string) => void;
  onCheckConsistency?: () => void;
};

export function MetadataPanel({
  note,
  graph,
  consistency,
  rating,
  onAddAnnotation,
  onCheckConsistency,
}: MetadataPanelProps) {
  const [annotationBody, setAnnotationBody] = useState("");

  if (!note) {
    return (
      <section className="metadata-panel">
        <h2>Metadata</h2>
        <p className="empty-state">No note selected</p>
      </section>
    );
  }

  return (
    <section className="metadata-panel">
      <h2>Metadata</h2>
      <dl className="metadata-list">
        <div>
          <dt>uuid</dt>
          <dd>{note.uuid}</dd>
        </div>
        <div>
          <dt>vault_path</dt>
          <dd>{note.vault_path}</dd>
        </div>
        <div>
          <dt>entity_type</dt>
          <dd>{note.entity_type}</dd>
        </div>
        <div>
          <dt>wiki_links</dt>
          <dd>{note.wiki_links.join(", ") || "None"}</dd>
        </div>
      </dl>

      <h2>Relationships</h2>
      <div className="relationship-list">
        {note.relationships.map((relationship) => (
          <div className="relationship-row" key={relationship.uuid ?? relationship.relationship_type}>
            <span className="relationship-row__type">{relationship.relationship_type}</span>
            <span className="relationship-row__target">
              {relationship.target_title ?? relationship.target_uuid ?? relationship.source_uuid}
            </span>
            <span className="relationship-row__entity">{relationship.direction ?? "linked"}</span>
          </div>
        ))}
      </div>

      <h2>Annotations</h2>
      <div className="annotation-list">
        {note.annotations.length ? (
          note.annotations.map((annotation) => (
            <article className="annotation-row" key={annotation.uuid}>
              <span>{annotation.author}</span>
              <p>{annotation.body}</p>
              <small>{annotation.created_at}</small>
            </article>
          ))
        ) : (
          <p className="empty-state">No annotations yet</p>
        )}
      </div>
      <form
        className="annotation-form"
        onSubmit={(event) => {
          event.preventDefault();
          if (!annotationBody.trim()) {
            return;
          }
          onAddAnnotation?.(annotationBody);
          setAnnotationBody("");
        }}
      >
        <label>
          <span className="section-label">Annotation</span>
          <textarea
            onChange={(event) => setAnnotationBody(event.target.value)}
            placeholder="Add a separate user note without changing the generated Markdown."
            value={annotationBody}
          />
        </label>
        <button className="primary-action" type="submit">
          <MessageSquarePlus aria-hidden="true" size={16} />
          Add annotation
        </button>
      </form>

      <div aria-label="Consistency">
        <ConsistencyPanel consistency={consistency ?? note.consistency} onCheckConsistency={onCheckConsistency} />
      </div>
      <div aria-label="Rating basis">
        <RatingBasisPanel rating={rating ?? note.rating} />
      </div>

      <h2>Graph focus</h2>
      <dl className="metadata-list">
        <div>
          <dt>nodes</dt>
          <dd>{graph?.nodes.length ?? 0}</dd>
        </div>
        <div>
          <dt>edges</dt>
          <dd>{graph?.edges.length ?? 0}</dd>
        </div>
      </dl>
    </section>
  );
}
