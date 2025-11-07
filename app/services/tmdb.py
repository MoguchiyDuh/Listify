from datetime import datetime
from typing import List, Literal, Optional

from app.core.config import settings
from app.core.logger import setup_logger
from app.models import MediaStatusEnum
from app.schemas.movie import MovieCreate
from app.schemas.series import SeriesCreate
from app.services.base import BaseAPIService

logger = setup_logger("tmdb")


class TMDBService(BaseAPIService):
    """Service for The Movie Database API."""

    def __init__(self):
        super().__init__(
            base_url="https://api.themoviedb.org/3",
            headers=(
                {"Authorization": f"Bearer {settings.TMDB_API_KEY}"}
                if settings.TMDB_API_KEY
                else {}
            ),
        )

    def _build_params(self, **kwargs) -> dict:
        """Build params with API key."""
        params = {**kwargs}
        return {k: v for k, v in params.items() if v is not None}

    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: Literal["movie", "tv", "multi"] = "multi",
    ) -> List[dict]:
        """Search movies or TV shows."""
        logger.info(f"Searching TMDB {media_type} for: {query} (limit: {limit})")
        params = self._build_params(
            query=query, include_adult="true", append_to_response="credits"
        )
        data = await self._get(f"search/{media_type}", params)
        results = data.get("results", [])[:limit] if data else []
        logger.debug(f"TMDB search returned {len(results)} results")
        return results

    async def get_by_id(
        self,
        media_id: str,
        media_type: Literal["movie", "tv"] = "movie",
    ) -> Optional[dict]:
        """Get movie or TV show details."""
        logger.info(f"Fetching TMDB {media_type} by ID: {media_id}")
        params = self._build_params(include_adult="true", append_to_response="credits")
        data = await self._get(f"{media_type}/{media_id}", params)
        if data:
            title = data.get("title") if media_type == "movie" else data.get("name")
            logger.debug(f"Found {media_type}: {title or 'Unknown'}")
        else:
            logger.warning(f"{media_type.upper()} not found with ID: {media_id}")
        return data

    def to_movie_create(self, tmdb_data: dict) -> MovieCreate:
        """Convert TMDB movie data to MovieCreate schema."""
        release_date = None
        if tmdb_data.get("release_date"):
            try:
                release_date = datetime.strptime(
                    tmdb_data["release_date"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                pass

        logger.debug(
            f"Converting TMDB movie data for: {tmdb_data.get('title', 'Unknown')}"
        )

        return MovieCreate(
            title=tmdb_data.get("title", "Unknown"),
            description=tmdb_data.get("overview"),
            release_date=release_date,
            cover_image_url=self.get_image_url(tmdb_data.get("poster_path")),
            external_id=str(tmdb_data.get("id")),
            external_source="tmdb",
            runtime=tmdb_data.get("runtime"),
        )

    def to_series_create(self, tmdb_data: dict) -> SeriesCreate:
        """Convert TMDB TV data to SeriesCreate schema."""
        status_map = {
            "Ended": MediaStatusEnum.FINISHED,
            "Returning Series": MediaStatusEnum.AIRING,
            "Canceled": MediaStatusEnum.CANCELLED,
            "Planned": MediaStatusEnum.UPCOMING,
            "In Production": MediaStatusEnum.AIRING,
        }

        first_air_date = None
        if tmdb_data.get("first_air_date"):
            try:
                first_air_date = datetime.strptime(
                    tmdb_data["first_air_date"], "%Y-%m-%d"
                ).date()
            except (ValueError, TypeError):
                pass

        logger.debug(
            f"Converting TMDB series data for: {tmdb_data.get('name', 'Unknown')}"
        )

        return SeriesCreate(
            title=tmdb_data.get("name", "Unknown"),
            description=tmdb_data.get("overview"),
            release_date=first_air_date,
            cover_image_url=self.get_image_url(tmdb_data.get("poster_path")),
            external_id=str(tmdb_data.get("id")),
            external_source="tmdb",
            total_episodes=tmdb_data.get("number_of_episodes"),
            seasons=tmdb_data.get("number_of_seasons"),
            status=status_map.get(tmdb_data.get("status"), MediaStatusEnum.FINISHED),
        )

    @staticmethod
    def get_image_url(path: Optional[str]) -> Optional[str]:
        """Build full image URL."""
        return f"https://image.tmdb.org/t/p/w500{path}" if path else None
