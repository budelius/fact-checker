import { useState } from "react";
import { BookOpenText } from "lucide-react";

import type { ReportVersion } from "../api/reports";
import { sampleNote, vaultSections, type VaultSectionName } from "../data/sampleVault";
import { IngestionWorkbench } from "./IngestionWorkbench";
import { MetadataPanel } from "./MetadataPanel";
import { ReportProvenancePanel } from "./reports/ReportProvenancePanel";
import { VaultNavigation } from "./VaultNavigation";

export function AppShell() {
  const [activeSection, setActiveSection] = useState<VaultSectionName>("Papers");
  const [activeReport, setActiveReport] = useState<ReportVersion | null>(null);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <BookOpenText aria-hidden="true" size={22} />
          <span>Fact Checker</span>
        </div>
        <div className="topbar__section">
          {activeReport ? "Fact-check report" : "TikTok ingestion"}
        </div>
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
        <IngestionWorkbench onReportChange={setActiveReport} />
      </main>

      <aside className="right-rail" aria-label={activeReport ? "Report provenance" : "Note metadata"}>
        {activeReport ? <ReportProvenancePanel report={activeReport} /> : <MetadataPanel note={sampleNote} />}
      </aside>
    </div>
  );
}
