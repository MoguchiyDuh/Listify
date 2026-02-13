from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Listify"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:////app/data/listify.db"

    @property
    def database_url_async(self) -> str:
        """Convert sync DB URL to async version with appropriate driver."""
        url = self.DATABASE_URL
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        elif url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost"

    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_SAMESITE: str = "lax"

    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600

    TMDB_API_KEY: Optional[str] = None

    IGDB_CLIENT_ID: Optional[str] = None
    IGDB_CLIENT_SECRET: Optional[str] = None
    IGDB_ACCESS_TOKEN: Optional[str] = None
    IGDB_TOKEN_EXPIRES_AT: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
