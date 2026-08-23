from __future__ import annotations

from functools import lru_cache

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    PROJECT_NAME: str = "business-platform"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # ── Postgres (discrete parts, assembled into a DSN below) ────────────────
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "business_platform"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Wide-open by default for dev; lock this down per-environment in prod.
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ── Rate limiting (in-memory sliding window) ─────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Redis (reserved for future multi-process rate limiting / workers) ────
    REDIS_URL: str = "redis://localhost:6379/0"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Accept a comma-separated string from the environment."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def _assemble_db_uri(cls, v: object, info) -> str:
        """Build the async Postgres DSN from discrete parts when not supplied."""
        if isinstance(v, str) and v:
            return v
        data = info.data
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_SERVER"),
            port=data.get("POSTGRES_PORT"),
            path=data.get("POSTGRES_DB") or "",
        )
        return str(dsn)


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so settings are parsed exactly once per process."""
    return Settings()


settings = get_settings()
