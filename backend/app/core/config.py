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
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    collectors: str = "binance"
    binance_ws_url: str = "wss://stream.binance.com:9443/stream"
    binance_symbols: str = "BTC,ETH"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def collector_list(self) -> list[str]:
        """Parse enabled collector names."""
        seen: set[str] = set()
        result: list[str] = []
        for name in self.collectors.split(","):
            normalized = name.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result

    @property
    def binance_symbol_list(self) -> list[str]:
        """Parse configured Binance base symbols."""
        return [
            symbol.strip().upper()
            for symbol in self.binance_symbols.split(",")
            if symbol.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
