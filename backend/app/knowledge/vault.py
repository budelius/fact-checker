import re
from collections import Counter
from pathlib import Path
from typing import Any
from uuid import UUID

import frontmatter

from app.schemas.entities import EntityType
from app.schemas.knowledge import (
    KnowledgeBacklink,
    KnowledgeNoteDetail,
    KnowledgeNoteListItem,
    KnowledgeRelationshipView,
    KnowledgeSection,
)

WIKI_LINK_RE = re.compile(r"\[\[([^\]#|]+)(?:[#|][^\]]*)?\]\]")


def _wiki_root(vault_root: Path) -> Path:
    if (vault_root / "wiki").exists():
        return vault_root / "wiki"
    if (vault_root / "vault" / "wiki").exists():
        return vault_root / "vault" / "wiki"
    return vault_root / "wiki"


def _vault_path(path: Path, vault_root: Path) -> str:
    try:
        return path.relative_to(vault_root).as_posix()
    except ValueError:
        return path.as_posix()


def _coerce_entity_type(value: Any, folder: str | None = None) -> EntityType:
    raw = str(value or (folder or "")).strip().lower()
    if raw.endswith("s"):
        singular = raw[:-1]
        if singular in EntityType._value2member_map_:
            return EntityType(singular)
    return EntityType(raw)


def _read_note(path: Path) -> tuple[dict[str, Any], str]:
    post = frontmatter.load(path)
    return dict(post.metadata), post.content.strip()


def extract_wiki_links(markdown: str) -> list[str]:
    return sorted({match.strip() for match in WIKI_LINK_RE.findall(markdown)})


def _iter_note_paths(vault_root: Path) -> list[Path]:
    wiki_root = _wiki_root(vault_root)
    if not wiki_root.exists():
        return []
    return sorted(wiki_root.glob("**/*.md"))


def _title_from_frontmatter(frontmatter_data: dict[str, Any], path: Path) -> str:
    return str(frontmatter_data.get("title") or frontmatter_data.get("slug") or path.stem)


def _excerpt(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped[:280]
    return ""


def _relationships_from_frontmatter(frontmatter_data: dict[str, Any]) -> list[KnowledgeRelationshipView]:
    relationships = []
    for item in frontmatter_data.get("relationships") or []:
        if not isinstance(item, dict):
            continue
        relationships.append(
            KnowledgeRelationshipView(
                uuid=item.get("uuid"),
                relationship_type=str(item.get("relationship_type") or item.get("type") or "related_to"),
                source_uuid=item.get("source_uuid"),
                target_uuid=item.get("target_uuid"),
                provenance=item.get("provenance"),
            )
        )
    return relationships


def _note_identity(path: Path, vault_root: Path) -> KnowledgeNoteListItem | None:
    frontmatter_data, body = _read_note(path)
    raw_uuid = frontmatter_data.get("uuid")
    if not raw_uuid:
        return None
    folder = path.parent.name
    try:
        entity_type = _coerce_entity_type(frontmatter_data.get("entity_type"), folder)
        note_uuid = UUID(str(raw_uuid))
    except (TypeError, ValueError):
        return None
    return KnowledgeNoteListItem(
        uuid=note_uuid,
        entity_type=entity_type,
        title=_title_from_frontmatter(frontmatter_data, path),
        vault_path=_vault_path(path, vault_root),
        slug=frontmatter_data.get("slug") or path.stem,
        excerpt=_excerpt(body),
        updated_at=frontmatter_data.get("updated_at"),
    )


def list_vault_sections(vault_root: Path) -> list[KnowledgeSection]:
    counts: Counter[EntityType] = Counter()
    for path in _iter_note_paths(vault_root):
        frontmatter_data, _body = _read_note(path)
        try:
            entity_type = _coerce_entity_type(frontmatter_data.get("entity_type"), path.parent.name)
        except ValueError:
            continue
        counts[entity_type] += 1

    return [
        KnowledgeSection(name=entity_type.value.title() + "s", entity_type=entity_type, count=count)
        for entity_type, count in sorted(counts.items(), key=lambda item: item[0].value)
    ]


def list_vault_notes(
    vault_root: Path,
    entity_type: EntityType | str | None = None,
) -> list[KnowledgeNoteListItem]:
    requested = EntityType(entity_type) if isinstance(entity_type, str) else entity_type
    notes = []
    for path in _iter_note_paths(vault_root):
        item = _note_identity(path, vault_root)
        if item is None:
            continue
        if requested is not None and item.entity_type != requested:
            continue
        notes.append(item)
    return notes


def _find_note_path(vault_root: Path, note_uuid: UUID | None, vault_path: str | None) -> Path | None:
    if vault_path:
        candidate = vault_root / vault_path
        if candidate.exists():
            return candidate
        candidate = vault_root.parent / vault_path
        if candidate.exists():
            return candidate

    if note_uuid is None:
        return None

    for path in _iter_note_paths(vault_root):
        frontmatter_data, _body = _read_note(path)
        if str(frontmatter_data.get("uuid")) == str(note_uuid):
            return path
    return None


def _build_backlinks(
    vault_root: Path,
    target_path: Path,
    target_uuid: UUID,
) -> list[KnowledgeBacklink]:
    backlinks: list[KnowledgeBacklink] = []
    wiki_root = _wiki_root(vault_root)
    target_link = target_path.relative_to(wiki_root).with_suffix("").as_posix()
    target_stem = target_path.stem
    for path in _iter_note_paths(vault_root):
        if path == target_path:
            continue
        frontmatter_data, body = _read_note(path)
        links = extract_wiki_links(body)
        if target_link not in links and target_stem not in links:
            continue
        item = _note_identity(path, vault_root)
        if item is None or item.uuid == target_uuid:
            continue
        backlinks.append(
            KnowledgeBacklink(
                uuid=item.uuid,
                entity_type=item.entity_type,
                title=item.title,
                vault_path=item.vault_path,
            )
        )
    return backlinks


def get_vault_note(
    vault_root: Path,
    note_uuid: UUID | None = None,
    vault_path: str | None = None,
) -> KnowledgeNoteDetail | None:
    path = _find_note_path(vault_root, note_uuid, vault_path)
    if path is None:
        return None

    frontmatter_data, body = _read_note(path)
    raw_uuid = frontmatter_data.get("uuid")
    if not raw_uuid:
        return None

    entity_uuid = UUID(str(raw_uuid))
    entity_type = _coerce_entity_type(frontmatter_data.get("entity_type"), path.parent.name)
    return KnowledgeNoteDetail(
        uuid=entity_uuid,
        entity_type=entity_type,
        title=_title_from_frontmatter(frontmatter_data, path),
        vault_path=_vault_path(path, vault_root),
        slug=frontmatter_data.get("slug") or path.stem,
        frontmatter=frontmatter_data,
        body_markdown=body,
        wiki_links=extract_wiki_links(body),
        relationships=_relationships_from_frontmatter(frontmatter_data),
        backlinks=_build_backlinks(vault_root, path, entity_uuid),
        updated_at=frontmatter_data.get("updated_at"),
    )
