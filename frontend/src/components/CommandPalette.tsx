import { Search, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { searchKnowledge, type KnowledgeSearchResult } from "../api/knowledge";

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
  onSelect: (result: KnowledgeSearchResult) => void;
  fallbackResults: KnowledgeSearchResult[];
};

export function CommandPalette({
  open,
  onClose,
  onSelect,
  fallbackResults,
}: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<KnowledgeSearchResult[]>(fallbackResults);

  useEffect(() => {
    if (!open) {
      return;
    }
    const handle = window.setTimeout(() => {
      if (!query.trim()) {
        setResults(fallbackResults);
        return;
      }
      searchKnowledge(query)
        .then((payload) => setResults(payload.results))
        .catch(() => {
          const lowered = query.toLowerCase();
          setResults(
            fallbackResults.filter((result) =>
              `${result.title} ${result.snippet} ${result.vault_path}`.toLowerCase().includes(lowered),
            ),
          );
        });
    }, 180);
    return () => window.clearTimeout(handle);
  }, [fallbackResults, open, query]);

  const groupedResults = useMemo(() => {
    return results.reduce<Record<string, KnowledgeSearchResult[]>>((groups, result) => {
      groups[result.entity_type] = groups[result.entity_type] ?? [];
      groups[result.entity_type].push(result);
      return groups;
    }, {});
  }, [results]);

  if (!open) {
    return null;
  }

  return (
    <div className="command-palette" role="dialog" aria-modal="true">
      <div className="command-palette__panel">
        <label className="command-palette__search">
          <Search aria-hidden="true" size={18} />
          <input
            autoFocus
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search the vault or jump to an entity"
            value={query}
          />
          <button aria-label="Close search" className="icon-button" onClick={onClose} type="button">
            <X aria-hidden="true" size={16} />
          </button>
        </label>

        {results.length === 0 ? (
          <div className="command-palette__empty">
            <strong>No matching knowledge found</strong>
            <p>Try a claim, paper title, creator, report UUID, or source URL.</p>
          </div>
        ) : (
          <div className="command-palette__results">
            {Object.entries(groupedResults).map(([entityType, group]) => (
              <section key={entityType}>
                <h2>{entityType}</h2>
                {group.map((result) => (
                  <button
                    className="command-result"
                    key={`${result.uuid}-${result.chunk_id ?? "note"}`}
                    onClick={() => onSelect(result)}
                    type="button"
                  >
                    <span>
                      <strong>{result.title}</strong>
                      <small>{result.entity_type}</small>
                    </span>
                    <span className="command-result__path">{result.vault_path || result.source}</span>
                    <p>{result.snippet}</p>
                  </button>
                ))}
              </section>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
