from uuid import UUID

from app.knowledge.annotations import (
    clear_annotations_for_tests,
    create_annotation,
    list_annotations_for_entity,
)
from app.knowledge.vault import get_vault_note, list_vault_notes, list_vault_sections
from app.schemas.entities import EntityType

PAPER_UUID = UUID("00000000-0000-4000-8000-000000000001")
CLAIM_UUID = UUID("00000000-0000-4000-8000-000000000002")


def setup_function(_function):
    clear_annotations_for_tests()


def _write_note(path, frontmatter: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter.strip()}\n---\n{body.strip()}\n", encoding="utf-8")


def _make_vault(tmp_path):
    vault = tmp_path / "vault"
    _write_note(
        vault / "wiki" / "papers" / "attention-is-all-you-need.md",
        f"""
uuid: {PAPER_UUID}
entity_type: paper
slug: attention-is-all-you-need
title: Attention Is All You Need
aliases: []
external_ids: []
relationships:
  - relationship_type: supports
    source_uuid: {PAPER_UUID}
    target_uuid: {CLAIM_UUID}
    provenance: report-v1
created_at: 2026-04-18T00:00:00Z
updated_at: 2026-04-18T00:00:00Z
""",
        """
# Summary

The paper supports [[claims/transformer-attention-scaling]].
""",
    )
    _write_note(
        vault / "wiki" / "claims" / "transformer-attention-scaling.md",
        f"""
uuid: {CLAIM_UUID}
entity_type: claim
slug: transformer-attention-scaling
title: Transformer attention scaling
aliases: []
external_ids: []
relationships: []
created_at: 2026-04-18T00:00:00Z
updated_at: 2026-04-18T00:00:00Z
""",
        """
# Claim

This claim cites [[papers/attention-is-all-you-need]].
""",
    )
    return vault


def test_list_vault_sections_counts_entity_folders(tmp_path):
    vault = _make_vault(tmp_path)

    sections = list_vault_sections(vault)

    counts = {section.entity_type: section.count for section in sections}
    assert counts[EntityType.paper] == 1
    assert counts[EntityType.claim] == 1


def test_note_detail_parses_frontmatter_body_links_and_backlinks(tmp_path):
    vault = _make_vault(tmp_path)

    note = get_vault_note(vault, note_uuid=PAPER_UUID)

    assert note is not None
    assert note.uuid == PAPER_UUID
    assert note.title == "Attention Is All You Need"
    assert note.entity_type == EntityType.paper
    assert "uuid" in note.frontmatter
    assert note.body_markdown.startswith("# Summary")
    assert note.wiki_links == ["claims/transformer-attention-scaling"]
    assert note.relationships[0].relationship_type == "supports"
    assert note.backlinks[0].uuid == CLAIM_UUID


def test_list_vault_notes_filters_by_entity_type(tmp_path):
    vault = _make_vault(tmp_path)

    notes = list_vault_notes(vault, entity_type=EntityType.paper)

    assert len(notes) == 1
    assert notes[0].uuid == PAPER_UUID
    assert notes[0].vault_path == "wiki/papers/attention-is-all-you-need.md"


def test_annotation_creation_does_not_change_markdown_file_content(tmp_path):
    vault = _make_vault(tmp_path)
    note_path = vault / "wiki" / "papers" / "attention-is-all-you-need.md"
    before = note_path.read_text(encoding="utf-8")

    annotation = create_annotation(PAPER_UUID, "User note about methods.")

    after = note_path.read_text(encoding="utf-8")
    annotations = list_annotations_for_entity(PAPER_UUID)
    assert annotation.author == "user"
    assert annotations[0].body == "User note about methods."
    assert after == before
