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


@lru_cache
def get_settings() -> Settings:
    return Settings()
