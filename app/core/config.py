from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./Listify.db"

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Mode
    DEBUG: bool = True

    # API Keys
    TMDB_API_KEY: Optional[str] = None
    IGDB_CLIENT_ID: Optional[str] = None
    IGDB_ACCESS_TOKEN: Optional[str] = None
    STEAM_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Create settings instance
settings = Settings()
