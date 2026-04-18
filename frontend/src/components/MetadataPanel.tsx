import type { VaultNote } from "../data/sampleVault";

type MetadataPanelProps = {
  note: VaultNote;
};

export function MetadataPanel({ note }: MetadataPanelProps) {
  return (
    <section className="metadata-panel">
      <h2>Metadata</h2>
      <dl className="metadata-list">
        <div>
          <dt>uuid</dt>
          <dd>{note.uuid}</dd>
        </div>
        <div>
          <dt>slug</dt>
          <dd>{note.slug}</dd>
        </div>
        <div>
          <dt>entity_type</dt>
          <dd>{note.entity_type}</dd>
        </div>
        <div>
          <dt>aliases</dt>
          <dd>{note.aliases.join(", ")}</dd>
        </div>
        <div>
          <dt>external_ids</dt>
          <dd>{note.external_ids.map((id) => `${id.provider}:${id.value}`).join(", ")}</dd>
        </div>
      </dl>

      <h2>relationships</h2>
      <div className="relationship-list">
        {note.relationships.map((relationship) => (
          <div className="relationship-row" key={`${relationship.type}-${relationship.targetLabel}`}>
            <span className="relationship-row__type">{relationship.type}</span>
            <span className="relationship-row__target">{relationship.targetLabel}</span>
            <span className="relationship-row__entity">{relationship.targetEntityType}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
