import type { LucideIcon } from "lucide-react";
import {
  BadgeCheck,
  ClipboardList,
  FileText,
  Link2,
  PenLine,
  Quote,
  Tags,
  UserRound,
  Video,
} from "lucide-react";

export type VaultSectionName =
  | "Videos"
  | "Creators"
  | "Claims"
  | "Papers"
  | "Authors"
  | "Sources"
  | "Evidence"
  | "Reports"
  | "Topics";

export type VaultSection = {
  name: VaultSectionName;
  count: number;
  icon: LucideIcon;
};

export type VaultRelationship = {
  type: "cites" | "supports" | "contradicts" | "authored_by" | "discussed_in";
  targetLabel: string;
  targetEntityType: string;
};

export type VaultNote = {
  uuid: string;
  entity_type: string;
  slug: string;
  title: string;
  aliases: string[];
  external_ids: Array<{ provider: string; value: string }>;
  relationships: VaultRelationship[];
  created_at: string;
  updated_at: string;
  wikiLinks: string[];
  excerpt: string;
};

export const vaultSections: VaultSection[] = [
  { name: "Videos", count: 0, icon: Video },
  { name: "Creators", count: 0, icon: UserRound },
  { name: "Claims", count: 1, icon: Quote },
  { name: "Papers", count: 1, icon: FileText },
  { name: "Authors", count: 1, icon: PenLine },
  { name: "Sources", count: 0, icon: Link2 },
  { name: "Evidence", count: 1, icon: BadgeCheck },
  { name: "Reports", count: 0, icon: ClipboardList },
  { name: "Topics", count: 0, icon: Tags },
];

export const sampleNote: VaultNote = {
  uuid: "00000000-0000-4000-8000-000000000001",
  entity_type: "paper",
  slug: "attention-is-all-you-need",
  title: "attention-is-all-you-need",
  aliases: ["Transformer paper", "Vaswani et al. 2017"],
  external_ids: [{ provider: "arxiv", value: "1706.03762" }],
  relationships: [
    {
      type: "cites",
      targetLabel: "Neural machine translation by jointly learning to align and translate",
      targetEntityType: "paper",
    },
    {
      type: "supports",
      targetLabel: "transformer-attention-scaling",
      targetEntityType: "claim",
    },
    {
      type: "authored_by",
      targetLabel: "ashish-vaswani",
      targetEntityType: "author",
    },
    {
      type: "discussed_in",
      targetLabel: "future-video-placeholder",
      targetEntityType: "video",
    },
  ],
  created_at: "2026-04-18T00:00:00Z",
  updated_at: "2026-04-18T00:00:00Z",
  wikiLinks: ["[[claims/transformer-attention-scaling]]", "[[authors/ashish-vaswani]]"],
  excerpt:
    "Sample vault note showing how a paper, claim, author, and evidence relationship will be represented once ingestion exists.",
};
