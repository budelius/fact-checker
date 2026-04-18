import { API_BASE_URL } from "./ingestion";

export type EntityType =
  | "video"
  | "creator"
  | "transcript"
  | "screenshot"
  | "claim"
  | "source"
  | "paper"
  | "author"
  | "evidence"
  | "report"
  | "rating"
  | "topic";

export type ConsistencyStatus = "synced" | "drift" | "broken";
export type RatingBadgeText =
  | "strong evidence history"
  | "mixed evidence history"
  | "limited evidence"
  | "insufficient history";

export type KnowledgeSection = {
  name: string;
  entity_type?: EntityType | null;
  count: number;
};

export type KnowledgeNoteListItem = {
  uuid: string;
  entity_type: EntityType;
  title: string;
  vault_path: string;
  slug?: string | null;
  excerpt: string;
  updated_at?: string | null;
};

export type KnowledgeRelationshipView = {
  uuid?: string | null;
  relationship_type: string;
  source_uuid?: string | null;
  target_uuid?: string | null;
  source_title?: string | null;
  target_title?: string | null;
  direction?: string | null;
  provenance?: string | null;
  vault_path?: string | null;
};

export type KnowledgeBacklink = {
  uuid: string;
  entity_type: EntityType;
  title: string;
  vault_path: string;
  relationship_type?: string | null;
};

export type KnowledgeAnnotation = {
  uuid: string;
  target_entity_uuid: string;
  author: string;
  body: string;
  created_at: string;
  updated_at: string;
};

export type KnowledgeRatingSummary = {
  rating_uuid?: string | null;
  target_uuid: string;
  target_entity_type: EntityType;
  title?: string | null;
  vault_path?: string | null;
  badge: RatingBadgeText;
  experimental: boolean;
  evidence_count: number;
  label_distribution: Record<string, number>;
  source_basis: string[];
  confidence_level: string;
  report_version_uuids: string[];
};

export type KnowledgeConsistencyIssue = {
  status: ConsistencyStatus;
  affected_uuid?: string | null;
  entity_type?: EntityType | null;
  title?: string | null;
  vault_path?: string | null;
  store: string;
  issue: string;
  suggested_repair: string;
};

export type KnowledgeConsistencySummary = {
  status: ConsistencyStatus;
  checked_notes: number;
  missing_mongo_records: number;
  missing_qdrant_payloads: number;
  broken_relationships: number;
  orphan_vectors: number;
  issues: KnowledgeConsistencyIssue[];
};

export type KnowledgeNoteDetail = {
  uuid: string;
  entity_type: EntityType;
  title: string;
  vault_path: string;
  slug?: string | null;
  frontmatter: Record<string, unknown>;
  body_markdown: string;
  wiki_links: string[];
  relationships: KnowledgeRelationshipView[];
  backlinks: KnowledgeBacklink[];
  annotations: KnowledgeAnnotation[];
  rating?: KnowledgeRatingSummary | null;
  consistency?: KnowledgeConsistencySummary | null;
  updated_at?: string | null;
};

export type KnowledgeSearchResult = {
  uuid: string;
  entity_type: EntityType;
  title: string;
  vault_path: string;
  snippet: string;
  score?: number | null;
  source?: string | null;
  chunk_id?: string | null;
  source_uuid?: string | null;
  relationship_uuid?: string | null;
  relationship_uuids: string[];
  vector_backed: boolean;
};

export type KnowledgeGraphNode = {
  uuid: string;
  entity_type: EntityType;
  title: string;
  vault_path?: string | null;
  degree: number;
};

export type KnowledgeGraphEdge = {
  uuid: string;
  relationship_type: string;
  source_uuid: string;
  target_uuid: string;
  provenance: string;
  direction: string;
};

export type KnowledgeGraphResponse = {
  selected_uuid: string;
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
  important_nodes: KnowledgeGraphNode[];
  clusters: Record<string, string[]>;
};

export type RatingRecord = {
  rating_uuid: string;
  target_uuid: string;
  target_entity_type: "creator" | "paper" | "author" | "source";
  target_title: string;
  badge: RatingBadgeText;
  experimental: boolean;
  evidence_count: number;
  label_distribution: Record<string, number>;
  source_basis: string[];
  confidence_level: "low" | "medium" | "high";
  report_version_uuids: string[];
  evidence_uuids: string[];
  relationship_uuids: string[];
  generated_at: string;
  vault_path: string;
};

async function parseResponse<T>(response: Response, fallbackError: string): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(typeof payload.detail === "string" ? payload.detail : fallbackError);
  }
  return response.json() as Promise<T>;
}

export async function fetchKnowledgeSections(): Promise<KnowledgeSection[]> {
  return parseResponse<KnowledgeSection[]>(
    await fetch(`${API_BASE_URL}/knowledge/sections`),
    "knowledge_sections_fetch_failed",
  );
}

export async function fetchKnowledgeNotes(entityType?: EntityType): Promise<KnowledgeNoteListItem[]> {
  const suffix = entityType ? `?entity_type=${encodeURIComponent(entityType)}` : "";
  return parseResponse<KnowledgeNoteListItem[]>(
    await fetch(`${API_BASE_URL}/knowledge/notes${suffix}`),
    "knowledge_notes_fetch_failed",
  );
}

export async function fetchKnowledgeNote(noteUuid: string): Promise<KnowledgeNoteDetail> {
  return parseResponse<KnowledgeNoteDetail>(
    await fetch(`${API_BASE_URL}/knowledge/notes/${noteUuid}`),
    "knowledge_note_fetch_failed",
  );
}

export async function createKnowledgeAnnotation(
  noteUuid: string,
  body: string,
): Promise<KnowledgeAnnotation> {
  return parseResponse<KnowledgeAnnotation>(
    await fetch(`${API_BASE_URL}/knowledge/notes/${noteUuid}/annotations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body }),
    }),
    "knowledge_annotation_create_failed",
  );
}

export async function searchKnowledge(
  query: string,
  entityTypes: EntityType[] = [],
): Promise<{ query: string; results: KnowledgeSearchResult[]; count: number; vector_backed: boolean }> {
  const params = new URLSearchParams({ q: query });
  entityTypes.forEach((entityType) => params.append("entity_type", entityType));
  return parseResponse(
    await fetch(`${API_BASE_URL}/knowledge/search?${params.toString()}`),
    "knowledge_search_failed",
  );
}

export async function fetchKnowledgeGraph(noteUuid: string): Promise<KnowledgeGraphResponse> {
  return parseResponse<KnowledgeGraphResponse>(
    await fetch(`${API_BASE_URL}/knowledge/graph/${noteUuid}`),
    "knowledge_graph_fetch_failed",
  );
}

export async function fetchKnowledgeConsistency(): Promise<KnowledgeConsistencySummary> {
  return parseResponse<KnowledgeConsistencySummary>(
    await fetch(`${API_BASE_URL}/knowledge/consistency`),
    "knowledge_consistency_fetch_failed",
  );
}

export async function fetchRating(targetUuid: string): Promise<RatingRecord> {
  return parseResponse<RatingRecord>(
    await fetch(`${API_BASE_URL}/knowledge/ratings/${targetUuid}`),
    "knowledge_rating_fetch_failed",
  );
}

export async function refreshRating(targetUuid: string): Promise<RatingRecord> {
  return parseResponse<RatingRecord>(
    await fetch(`${API_BASE_URL}/knowledge/ratings/${targetUuid}/refresh`, {
      method: "POST",
    }),
    "knowledge_rating_refresh_failed",
  );
}
