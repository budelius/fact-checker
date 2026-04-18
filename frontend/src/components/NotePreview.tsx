import type { VaultNote, VaultSectionName } from "../data/sampleVault";

type NotePreviewProps = {
  activeSection: VaultSectionName;
  note: VaultNote;
};

export function NotePreview({ activeSection, note }: NotePreviewProps) {
  const frontmatter = [
    `uuid: ${note.uuid}`,
    `entity_type: ${note.entity_type}`,
    `slug: ${note.slug}`,
    `title: ${note.title}`,
    `aliases: [${note.aliases.join(", ")}]`,
    `external_ids: ${note.external_ids.map((id) => `${id.provider}:${id.value}`).join(", ")}`,
    `relationships: ${note.relationships.map((relationship) => relationship.type).join(", ")}`,
    `created_at: ${note.created_at}`,
    `updated_at: ${note.updated_at}`,
  ];

  return (
    <article className="note-preview">
      <div className="note-preview__meta">
        <span>{activeSection}</span>
        <span>{note.updated_at}</span>
      </div>
      <h1>{note.title}</h1>
      <p className="note-preview__type">{note.entity_type}</p>

      <pre className="frontmatter" aria-label="Frontmatter preview">
        {frontmatter.join("\n")}
      </pre>

      <section className="note-preview__body">
        <h2>Summary</h2>
        <p>{note.excerpt}</p>
        <h2>Links</h2>
        <ul>
          {note.wikiLinks.map((link) => (
            <li key={link}>
              <code>{link}</code>
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
