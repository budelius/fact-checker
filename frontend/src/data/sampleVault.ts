import type { LucideIcon } from "lucide-react";
import {
  BadgeCheck,
  ClipboardList,
  FileText,
  Link2,
  PenLine,
  Quote,
  ShieldCheck,
  Sparkles,
  Tags,
  UserRound,
  Video,
} from "lucide-react";

import type {
  KnowledgeAnnotation,
  KnowledgeConsistencySummary,
  KnowledgeGraphResponse,
  KnowledgeNoteDetail,
  KnowledgeRatingSummary,
  KnowledgeSection,
  RatingRecord,
} from "../api/knowledge";

export type VaultSectionName =
  | "Videos"
  | "Creators"
  | "Claims"
  | "Papers"
  | "Authors"
  | "Sources"
  | "Evidence"
  | "Reports"
  | "Ratings"
  | "Topics";

export type VaultSection = KnowledgeSection & {
  name: VaultSectionName;
  icon: LucideIcon;
};

export const vaultSections: VaultSection[] = [
  { name: "Videos", entity_type: "video", count: 0, icon: Video },
  { name: "Creators", entity_type: "creator", count: 0, icon: UserRound },
  { name: "Claims", entity_type: "claim", count: 1, icon: Quote },
  { name: "Papers", entity_type: "paper", count: 1, icon: FileText },
  { name: "Authors", entity_type: "author", count: 1, icon: PenLine },
  { name: "Sources", entity_type: "source", count: 0, icon: Link2 },
  { name: "Evidence", entity_type: "evidence", count: 1, icon: BadgeCheck },
  { name: "Reports", entity_type: "report", count: 0, icon: ClipboardList },
  { name: "Ratings", entity_type: "rating", count: 1, icon: ShieldCheck },
  { name: "Topics", entity_type: "topic", count: 0, icon: Tags },
];

export const sampleAnnotation: KnowledgeAnnotation = {
  uuid: "00000000-0000-4000-8000-000000000101",
  target_entity_uuid: "00000000-0000-4000-8000-000000000001",
  author: "user",
  body: "Review the methods section when a follow-up report compares scaling claims.",
  created_at: "2026-04-18T00:00:00Z",
  updated_at: "2026-04-18T00:00:00Z",
};

export const sampleRatingSummary: KnowledgeRatingSummary = {
  rating_uuid: "00000000-0000-4000-8000-000000000201",
  target_uuid: "00000000-0000-4000-8000-000000000001",
  target_entity_type: "paper",
  title: "Attention Is All You Need",
  vault_path: "vault/wiki/ratings/paper-attention-is-all-you-need.md",
  badge: "strong evidence history",
  experimental: false,
  evidence_count: 12,
  label_distribution: {
    supported: 10,
    contradicted: 1,
    mixed: 1,
    insufficient: 0,
  },
  source_basis: ["vault/wiki/reports/transformer-attention-report-v1.md"],
  confidence_level: "high",
  report_version_uuids: ["00000000-0000-4000-8000-000000000301"],
};

export const sampleRatingRecord: RatingRecord = {
  rating_uuid: sampleRatingSummary.rating_uuid ?? "",
  target_uuid: sampleRatingSummary.target_uuid,
  target_entity_type: "paper",
  target_title: "Attention Is All You Need",
  badge: "strong evidence history",
  experimental: false,
  evidence_count: 12,
  label_distribution: sampleRatingSummary.label_distribution,
  source_basis: sampleRatingSummary.source_basis,
  confidence_level: "high",
  report_version_uuids: sampleRatingSummary.report_version_uuids,
  evidence_uuids: ["00000000-0000-4000-8000-000000000302"],
  relationship_uuids: ["00000000-0000-4000-8000-000000000004"],
  generated_at: "2026-04-18T00:00:00Z",
  vault_path: sampleRatingSummary.vault_path ?? "",
};

export const sampleConsistency: KnowledgeConsistencySummary = {
  status: "synced",
  checked_notes: 18,
  missing_mongo_records: 0,
  missing_qdrant_payloads: 0,
  broken_relationships: 0,
  orphan_vectors: 0,
  issues: [],
};

export const sampleGraph: KnowledgeGraphResponse = {
  selected_uuid: "00000000-0000-4000-8000-000000000001",
  nodes: [
    {
      uuid: "00000000-0000-4000-8000-000000000001",
      entity_type: "paper",
      title: "Attention Is All You Need",
      vault_path: "wiki/papers/attention-is-all-you-need.md",
      degree: 3,
    },
    {
      uuid: "00000000-0000-4000-8000-000000000002",
      entity_type: "claim",
      title: "Transformer attention scaling",
      vault_path: "wiki/claims/transformer-attention-scaling.md",
      degree: 1,
    },
    {
      uuid: "00000000-0000-4000-8000-000000000003",
      entity_type: "author",
      title: "Ashish Vaswani",
      vault_path: "wiki/authors/ashish-vaswani.md",
      degree: 1,
    },
  ],
  edges: [
    {
      uuid: "00000000-0000-4000-8000-000000000004",
      relationship_type: "supports",
      source_uuid: "00000000-0000-4000-8000-000000000001",
      target_uuid: "00000000-0000-4000-8000-000000000002",
      provenance: "report-v1",
      direction: "outgoing",
    },
    {
      uuid: "00000000-0000-4000-8000-000000000005",
      relationship_type: "authored_by",
      source_uuid: "00000000-0000-4000-8000-000000000001",
      target_uuid: "00000000-0000-4000-8000-000000000003",
      provenance: "paper metadata",
      direction: "outgoing",
    },
  ],
  important_nodes: [
    {
      uuid: "00000000-0000-4000-8000-000000000001",
      entity_type: "paper",
      title: "Attention Is All You Need",
      vault_path: "wiki/papers/attention-is-all-you-need.md",
      degree: 3,
    },
  ],
  clusters: {
    paper: ["00000000-0000-4000-8000-000000000001"],
    claim: ["00000000-0000-4000-8000-000000000002"],
    author: ["00000000-0000-4000-8000-000000000003"],
  },
};

export const sampleNote: KnowledgeNoteDetail = {
  uuid: "00000000-0000-4000-8000-000000000001",
  entity_type: "paper",
  slug: "attention-is-all-you-need",
  title: "Attention Is All You Need",
  vault_path: "wiki/papers/attention-is-all-you-need.md",
  frontmatter: {
    uuid: "00000000-0000-4000-8000-000000000001",
    entity_type: "paper",
    slug: "attention-is-all-you-need",
    title: "Attention Is All You Need",
    aliases: ["Transformer paper", "Vaswani et al. 2017"],
  },
  body_markdown:
    "# Summary\n\nSample vault note showing how a paper, claim, author, and evidence relationship is represented once ingestion exists.\n\n## Evidence trail\n\n- Supports [[claims/transformer-attention-scaling]].\n- Authored by [[authors/ashish-vaswani]].\n- Indexed from reusable source chunks.",
  wiki_links: ["claims/transformer-attention-scaling", "authors/ashish-vaswani"],
  relationships: [
    {
      uuid: "00000000-0000-4000-8000-000000000004",
      relationship_type: "supports",
      source_uuid: "00000000-0000-4000-8000-000000000001",
      target_uuid: "00000000-0000-4000-8000-000000000002",
      target_title: "Transformer attention scaling",
      direction: "outgoing",
      provenance: "report-v1",
    },
    {
      uuid: "00000000-0000-4000-8000-000000000005",
      relationship_type: "authored_by",
      source_uuid: "00000000-0000-4000-8000-000000000001",
      target_uuid: "00000000-0000-4000-8000-000000000003",
      target_title: "Ashish Vaswani",
      direction: "outgoing",
      provenance: "paper metadata",
    },
  ],
  backlinks: [
    {
      uuid: "00000000-0000-4000-8000-000000000002",
      entity_type: "claim",
      title: "Transformer attention scaling",
      vault_path: "wiki/claims/transformer-attention-scaling.md",
      relationship_type: "supports",
    },
  ],
  annotations: [sampleAnnotation],
  rating: sampleRatingSummary,
  consistency: sampleConsistency,
  updated_at: "2026-04-18T00:00:00Z",
};

export const sampleSearchIcon = Sparkles;
