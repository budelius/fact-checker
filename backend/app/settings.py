from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_database: str = Field(alias="MONGODB_DATABASE")
    qdrant_url: str = Field(alias="QDRANT_URL")
    qdrant_collection_knowledge: str = Field(alias="QDRANT_COLLECTION_KNOWLEDGE")
    vault_root: str = Field(alias="VAULT_ROOT")
    log_level: str = Field(alias="LOG_LEVEL")
    tiktok_media_download_enabled: bool = Field(
        default=False,
        alias="TIKTOK_MEDIA_DOWNLOAD_ENABLED",
    )
    tiktok_max_video_mb: int = Field(default=200, alias="TIKTOK_MAX_VIDEO_MB")
    transcription_provider: str = Field(default="disabled", alias="TRANSCRIPTION_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_discovery_model: str = Field(
        default="gpt-5.4-mini",
        alias="OPENAI_DISCOVERY_MODEL",
    )
    openai_summary_model: str = Field(
        default="gpt-5.4-mini",
        alias="OPENAI_SUMMARY_MODEL",
    )
    openai_evaluation_model: str = Field(
        default="gpt-5.4-mini",
        alias="OPENAI_EVALUATION_MODEL",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_embedding_dimensions: int | None = Field(
        default=None,
        alias="OPENAI_EMBEDDING_DIMENSIONS",
    )
    openalex_email: str | None = Field(default=None, alias="OPENALEX_EMAIL")
    semantic_scholar_api_key: str | None = Field(
        default=None,
        alias="SEMANTIC_SCHOLAR_API_KEY",
    )
    ground_truth_max_results_per_provider: int = Field(
        default=10,
        alias="GROUND_TRUTH_MAX_RESULTS_PER_PROVIDER",
    )
    paper_download_enabled: bool = Field(default=True, alias="PAPER_DOWNLOAD_ENABLED")
    paper_max_pdf_mb: int = Field(default=40, alias="PAPER_MAX_PDF_MB")
    paper_request_timeout_seconds: float = Field(
        default=20.0,
        alias="PAPER_REQUEST_TIMEOUT_SECONDS",
    )
    evaluation_max_chunks_per_claim: int = Field(
        default=8,
        alias="EVALUATION_MAX_CHUNKS_PER_CLAIM",
    )
    evaluation_excerpt_max_chars: int = Field(
        default=1200,
        alias="EVALUATION_EXCERPT_MAX_CHARS",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
