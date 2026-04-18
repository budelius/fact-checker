import { useState } from "react";
import { BookOpenText } from "lucide-react";

import { sampleNote, vaultSections, type VaultSectionName } from "../data/sampleVault";
import { MetadataPanel } from "./MetadataPanel";
import { NotePreview } from "./NotePreview";
import { VaultNavigation } from "./VaultNavigation";

export function AppShell() {
  const [activeSection, setActiveSection] = useState<VaultSectionName>("Papers");

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <BookOpenText aria-hidden="true" size={22} />
          <span>Fact Checker</span>
        </div>
        <div className="topbar__section">Knowledge Vault</div>
        <button className="topbar__button" type="button">
          Browse vault
        </button>
      </header>

      <aside className="left-rail" aria-label="Knowledge Vault">
        <VaultNavigation
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          sections={vaultSections}
        />
      </aside>

      <main className="main-pane">
        <NotePreview activeSection={activeSection} note={sampleNote} />
      </main>

      <aside className="right-rail" aria-label="Note metadata">
        <MetadataPanel note={sampleNote} />
      </aside>
    </div>
  );
}
