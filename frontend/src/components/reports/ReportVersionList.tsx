import type { ReportVersion } from "../../api/reports";

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export function ReportVersionList({
  versions,
  activeReportUuid,
}: {
  versions: ReportVersion[];
  activeReportUuid?: string | null;
}) {
  if (!versions.length) {
    return null;
  }

  return (
    <section className="ingestion-panel report-section">
      <h2>Report versions</h2>
      <div className="report-version-list">
        {versions.map((version) => (
          <article
            className={`report-version-row${
              version.report_uuid === activeReportUuid ? " report-version-row--active" : ""
            }`}
            key={version.report_uuid}
          >
            <strong>v{version.version}</strong>
            <span>{version.report_uuid}</span>
            <small>{formatDate(version.created_at)}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
