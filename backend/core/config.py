from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Listify"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./listify.db"

    # Security
    SECRET_KEY: str = "secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Cookie Security
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: Optional[str] = None  # None = same domain, "localhost" for local dev, IP for network access

    # API Keys
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
