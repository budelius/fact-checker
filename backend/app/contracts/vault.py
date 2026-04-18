VAULT_WIKI_ENTITY_FOLDERS = (
    "videos",
    "creators",
    "claims",
    "papers",
    "authors",
    "sources",
    "evidence",
    "reports",
    "topics",
)

REQUIRED_FRONTMATTER_KEYS = (
    "uuid",
    "entity_type",
    "slug",
    "title",
    "relationships",
    "created_at",
    "updated_at",
)


def expected_wiki_path(entity_type: str, slug: str) -> str:
    return f"vault/wiki/{entity_type}/{slug}.md"
