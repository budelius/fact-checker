VAULT_WIKI_ENTITY_FOLDERS = (
    "videos",
    "creators",
    "transcripts",
    "screenshots",
    "claims",
    "papers",
    "authors",
    "sources",
    "evidence",
    "reports",
    "topics",
)

VAULT_RAW_ARTIFACT_FOLDERS = ("videos", "transcripts", "screenshots")

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


def expected_raw_artifact_path(kind: str, slug: str, extension: str) -> str:
    normalized_extension = extension.lstrip(".")
    return f"vault/raw/{kind}/{slug}.{normalized_extension}"
