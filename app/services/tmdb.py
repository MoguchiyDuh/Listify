from datetime import datetime
from typing import List, Optional

from app.core.config import settings
from app.schemas.movie import MovieCreate
from app.schemas.series import SeriesCreate
from app.services.base import BaseAPIService


class TMDBService(BaseAPIService):
    """Service for The Movie Database API."""

    def __init__(self):
        super().__init__(
            base_url="https://api.themoviedb.org/3",
            api_key=settings.TMDB_API_KEY,
            timeout=15,
        )

    def _build_params(self, **kwargs) -> dict:
        """Build params with API key."""
        params = {"api_key": self.api_key, **kwargs}
        return {k: v for k, v in params.items() if v is not None}

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search for movies and TV shows."""
        params = self._build_params(query=query)
        data = await self._get("search/multi", params)

        if not data or "results" not in data:
            return []

        return [
            r for r in data["results"][:limit] if r.get("media_type") in ["movie", "tv"]
        ]

    async def get_details(self, media_id: str) -> Optional[dict]:
        """Get movie details."""
        params = self._build_params(append_to_response="credits")
        return await self._get(f"movie/{media_id}", params)

    async def search_movies(self, query: str, limit: int = 10) -> List[dict]:
        """Search movies."""
        params = self._build_params(query=query)
        data = await self._get("search/movie", params)
        return data.get("results", [])[:limit] if data else []

    async def search_tv(self, query: str, limit: int = 10) -> List[dict]:
        """Search TV shows."""
        params = self._build_params(query=query)
        data = await self._get("search/tv", params)
        return data.get("results", [])[:limit] if data else []

    async def get_movie_details(self, movie_id: str) -> Optional[dict]:
        """Get detailed movie info."""
        params = self._build_params(append_to_response="credits")
        return await self._get(f"movie/{movie_id}", params)

    async def get_tv_details(self, tv_id: str) -> Optional[dict]:
        """Get detailed TV show info."""
        params = self._build_params(append_to_response="credits")
        return await self._get(f"tv/{tv_id}", params)

    def to_movie_create(self, tmdb_data: dict) -> MovieCreate:
        """Convert TMDB movie data to MovieCreate schema."""
        director = None
        if "credits" in tmdb_data and "crew" in tmdb_data["credits"]:
            directors = [
                c["name"]
                for c in tmdb_data["credits"]["crew"]
                if c["job"] == "Director"
            ]
            director = directors[0] if directors else None

        return MovieCreate(
            title=tmdb_data.get("title", "Unknown"),
            description=tmdb_data.get("overview"),
            release_date=(
                datetime.strptime(tmdb_data["release_date"], "%Y-%m-%d").date()
                if tmdb_data.get("release_date")
                else None
            ),
            image=self.get_image_url(tmdb_data.get("poster_path")),
            runtime=tmdb_data.get("runtime"),
            director=director,
            is_custom=False,
        )

    def to_series_create(self, tmdb_data: dict) -> SeriesCreate:
        """Convert TMDB TV data to SeriesCreate schema."""
        from app.models.media import AnimeSeriesStatusEnum

        status_map = {
            "Ended": AnimeSeriesStatusEnum.FINISHED,
            "Returning Series": AnimeSeriesStatusEnum.AIRING,
            "Canceled": AnimeSeriesStatusEnum.FINISHED,
        }

        return SeriesCreate(
            title=tmdb_data.get("name", "Unknown"),
            description=tmdb_data.get("overview"),
            release_date=(
                datetime.strptime(tmdb_data["first_air_date"], "%Y-%m-%d").date()
                if tmdb_data.get("first_air_date")
                else None
            ),
            image=self.get_image_url(tmdb_data.get("poster_path")),
            total_episodes=tmdb_data.get("number_of_episodes"),
            seasons=tmdb_data.get("number_of_seasons"),
            status=status_map.get(
                tmdb_data.get("status"), AnimeSeriesStatusEnum.FINISHED
            ),
            is_custom=False,
        )

    @staticmethod
    def get_image_url(path: Optional[str]) -> Optional[str]:
        """Build full image URL."""
        return f"https://image.tmdb.org/t/p/w500{path}" if path else None
