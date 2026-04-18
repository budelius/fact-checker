import { GitBranch } from "lucide-react";
import { useMemo, useState } from "react";

import type { KnowledgeGraphEdge, KnowledgeGraphResponse } from "../api/knowledge";

type KnowledgeGraphPanelProps = {
  graph?: KnowledgeGraphResponse | null;
};

export function KnowledgeGraphPanel({ graph }: KnowledgeGraphPanelProps) {
  const [selectedEdge, setSelectedEdge] = useState<KnowledgeGraphEdge | null>(null);
  const nodeByUuid = useMemo(
    () => new Map((graph?.nodes ?? []).map((node) => [node.uuid, node])),
    [graph],
  );

  if (!graph || graph.edges.length === 0) {
    return (
      <section className="knowledge-graph">
        <h2>Graph</h2>
        <p className="empty-state">No relationships recorded yet</p>
      </section>
    );
  }

  const activeEdge = selectedEdge ?? graph.edges[0];

  return (
    <section className="knowledge-graph">
      <div className="panel-heading">
        <h2>Graph</h2>
        <span>{graph.nodes.length} nodes</span>
      </div>
      <div className="knowledge-graph__nodes">
        {graph.nodes.map((node) => (
          <span className="graph-node" key={node.uuid} title={node.uuid}>
            <GitBranch aria-hidden="true" size={14} />
            {node.title}
          </span>
        ))}
      </div>
      <div className="relationship-list">
        {graph.edges.map((edge) => (
          <button
            className="relationship-row relationship-row--button"
            key={edge.uuid}
            onClick={() => setSelectedEdge(edge)}
            type="button"
          >
            <span className="relationship-row__type">{edge.relationship_type}</span>
            <span className="relationship-row__target">
              {nodeByUuid.get(edge.source_uuid)?.title ?? edge.source_uuid} to{" "}
              {nodeByUuid.get(edge.target_uuid)?.title ?? edge.target_uuid}
            </span>
            <span className="relationship-row__entity">{edge.direction}</span>
          </button>
        ))}
      </div>
      <dl className="metadata-list graph-detail">
        <div>
          <dt>relationship_type</dt>
          <dd>{activeEdge.relationship_type}</dd>
        </div>
        <div>
          <dt>provenance</dt>
          <dd>{activeEdge.provenance}</dd>
        </div>
        <div>
          <dt>relationship_uuid</dt>
          <dd>{activeEdge.uuid}</dd>
        </div>
      </dl>
    </section>
  );
}
