"""Pydantic settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """OpenPulse application configuration."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
    )

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 15
    refresh_token_expire: int = 7
    env: str = "development"
    log_level: str = "INFO"
    app_version: str = "0.1.0"
    default_org_name: str = "default"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
