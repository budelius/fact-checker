import { BookOpenText, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  createKnowledgeAnnotation,
  fetchKnowledgeConsistency,
  fetchKnowledgeGraph,
  fetchKnowledgeNote,
  fetchKnowledgeNotes,
  fetchKnowledgeSections,
  fetchRating,
  type KnowledgeNoteDetail,
  type KnowledgeRatingSummary,
  type KnowledgeSearchResult,
} from "../api/knowledge";
import {
  sampleConsistency,
  sampleGraph,
  sampleNote,
  sampleRatingSummary,
  vaultSections,
  type VaultSection,
  type VaultSectionName,
} from "../data/sampleVault";
import { CommandPalette } from "./CommandPalette";
import { MetadataPanel } from "./MetadataPanel";
import { NotePreview } from "./NotePreview";
import { VaultNavigation } from "./VaultNavigation";

export function AppShell() {
  const [sections, setSections] = useState<VaultSection[]>(vaultSections);
  const [activeSection, setActiveSection] = useState<VaultSectionName>("Papers");
  const [selectedNote, setSelectedNote] = useState<KnowledgeNoteDetail | null>(sampleNote);
  const [graph, setGraph] = useState(sampleGraph);
  const [consistency, setConsistency] = useState(sampleConsistency);
  const [rating, setRating] = useState<KnowledgeRatingSummary | null>(sampleRatingSummary);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchKnowledgeSections()
      .then((remoteSections) => {
        setSections((current) =>
          current.map((section) => {
            const remote = remoteSections.find((item) => item.entity_type === section.entity_type);
            return remote ? { ...section, count: remote.count } : section;
          }),
        );
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    const entityType = sections.find((section) => section.name === activeSection)?.entity_type ?? undefined;
    if (!entityType) {
      return;
    }
    fetchKnowledgeNotes(entityType)
      .then((notes) => {
        if (notes[0]) {
          return fetchKnowledgeNote(notes[0].uuid);
        }
        return null;
      })
      .then((note) => {
        if (note) {
          setSelectedNote(note);
        }
      })
      .catch(() => undefined);
  }, [activeSection, sections]);

  useEffect(() => {
    if (!selectedNote) {
      return;
    }
    setLoading(true);
    Promise.allSettled([
      fetchKnowledgeGraph(selectedNote.uuid),
      fetchKnowledgeConsistency(),
      fetchRating(selectedNote.uuid),
    ]).then(([graphResult, consistencyResult, ratingResult]) => {
      if (graphResult.status === "fulfilled") {
        setGraph(graphResult.value);
      }
      if (consistencyResult.status === "fulfilled") {
        setConsistency(consistencyResult.value);
      }
      if (ratingResult.status === "fulfilled") {
        setRating({
          rating_uuid: ratingResult.value.rating_uuid,
          target_uuid: ratingResult.value.target_uuid,
          target_entity_type: ratingResult.value.target_entity_type,
          title: ratingResult.value.target_title,
          vault_path: ratingResult.value.vault_path,
          badge: ratingResult.value.badge,
          experimental: ratingResult.value.experimental,
          evidence_count: ratingResult.value.evidence_count,
          label_distribution: ratingResult.value.label_distribution,
          source_basis: ratingResult.value.source_basis,
          confidence_level: ratingResult.value.confidence_level,
          report_version_uuids: ratingResult.value.report_version_uuids,
        });
      }
      setLoading(false);
    });
  }, [selectedNote]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setPaletteOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const fallbackResults = useMemo<KnowledgeSearchResult[]>(
    () =>
      selectedNote
        ? [
            {
              uuid: selectedNote.uuid,
              entity_type: selectedNote.entity_type,
              title: selectedNote.title,
              vault_path: selectedNote.vault_path,
              snippet: selectedNote.body_markdown.slice(0, 220),
              relationship_uuids: selectedNote.relationships
                .map((relationship) => relationship.uuid)
                .filter((uuid): uuid is string => Boolean(uuid)),
              vector_backed: false,
            },
          ]
        : [],
    [selectedNote],
  );

  function openSearchResult(result: KnowledgeSearchResult) {
    fetchKnowledgeNote(result.uuid)
      .then(setSelectedNote)
      .catch(() =>
        setSelectedNote({
          uuid: result.uuid,
          entity_type: result.entity_type,
          title: result.title,
          vault_path: result.vault_path,
          frontmatter: {},
          body_markdown: result.snippet,
          wiki_links: [],
          relationships: [],
          backlinks: [],
          annotations: [],
        }),
      );
    setPaletteOpen(false);
  }

  function addAnnotation(body: string) {
    if (!selectedNote) {
      return;
    }
    createKnowledgeAnnotation(selectedNote.uuid, body)
      .then((annotation) =>
        setSelectedNote((note) =>
          note ? { ...note, annotations: [...note.annotations, annotation] } : note,
        ),
      )
      .catch(() =>
        setSelectedNote((note) =>
          note
            ? {
                ...note,
                annotations: [
                  ...note.annotations,
                  {
                    uuid: `${note.uuid}-local-${note.annotations.length}`,
                    target_entity_uuid: note.uuid,
                    author: "user",
                    body,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                  },
                ],
              }
            : note,
        ),
      );
  }

  function checkConsistency() {
    fetchKnowledgeConsistency().then(setConsistency).catch(() => undefined);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <BookOpenText aria-hidden="true" size={22} />
          <span>Fact Checker</span>
        </div>
        <div className="topbar__section">{loading ? "Loading vault page" : "Knowledge vault"}</div>
        <button className="topbar__button" onClick={() => setPaletteOpen(true)} type="button">
          <Search aria-hidden="true" size={16} />
          Search
        </button>
      </header>

      <aside className="left-rail" aria-label="Knowledge Vault">
        <VaultNavigation
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          sections={sections}
        />
      </aside>

      <main className="main-pane">
        <NotePreview
          consistency={consistency}
          graph={graph}
          note={selectedNote}
          onCheckConsistency={checkConsistency}
          rating={rating}
        />
      </main>

      <aside className="right-rail" aria-label="Note metadata">
        <MetadataPanel
          consistency={consistency}
          graph={graph}
          note={selectedNote}
          onAddAnnotation={addAnnotation}
          onCheckConsistency={checkConsistency}
          rating={rating}
        />
      </aside>

      <CommandPalette
        fallbackResults={fallbackResults}
        onClose={() => setPaletteOpen(false)}
        onSelect={openSearchResult}
        open={paletteOpen}
      />
    </div>
  );
}
