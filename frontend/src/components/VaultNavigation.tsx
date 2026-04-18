import type { VaultSection, VaultSectionName } from "../data/sampleVault";

type VaultNavigationProps = {
  activeSection: VaultSectionName;
  onSectionChange: (section: VaultSectionName) => void;
  sections: VaultSection[];
};

export function VaultNavigation({
  activeSection,
  onSectionChange,
  sections,
}: VaultNavigationProps) {
  return (
    <nav className="vault-nav" aria-label="Vault sections">
      {sections.map((section) => {
        const Icon = section.icon;
        const isActive = activeSection === section.name;

        return (
          <button
            aria-label={`${section.name} section${section.name === "Ratings" ? " for Ratings" : ""}`}
            aria-pressed={isActive}
            className={`vault-nav__item${isActive ? " vault-nav__item--active" : ""}`}
            key={section.name}
            onClick={() => onSectionChange(section.name)}
            type="button"
          >
            <Icon aria-hidden="true" size={18} />
            <span className="vault-nav__label">{section.name}</span>
            <span className="vault-nav__count">{section.count}</span>
          </button>
        );
      })}
    </nav>
  );
}
