from datetime import datetime
from typing import List, Optional

from app.schemas.anime import AnimeCreate
from app.services.base import BaseAPIService


class JikanService(BaseAPIService):
    """Service for Jikan API (MyAnimeList)."""

    def __init__(self):
        super().__init__(base_url="https://api.jikan.moe/v4", timeout=15)

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search anime."""
        params = {"q": query, "limit": limit, "sfw": True}
        data = await self._get("anime", params)
        return data.get("data", []) if data else []

    async def get_details(self, anime_id: str) -> Optional[dict]:
        """Get anime details."""
        data = await self._get(f"anime/{anime_id}/full")
        return data.get("data") if data else None

    def to_anime_create(self, jikan_data: dict) -> AnimeCreate:
        """Convert Jikan data to AnimeCreate schema."""
        from app.models.media import AnimeSeriesStatusEnum

        status_map = {
            "Finished Airing": AnimeSeriesStatusEnum.FINISHED,
            "Currently Airing": AnimeSeriesStatusEnum.AIRING,
            "Not yet aired": AnimeSeriesStatusEnum.UPCOMING,
        }

        studio = None
        if "studios" in jikan_data and jikan_data["studios"]:
            studio = jikan_data["studios"][0].get("name")

        aired = jikan_data.get("aired", {})
        release_date = None
        if aired.get("from"):
            release_date = datetime.fromisoformat(
                aired["from"].replace("Z", "+00:00")
            ).date()

        return AnimeCreate(
            title=jikan_data.get("title", "Unknown"),
            description=jikan_data.get("synopsis"),
            release_date=release_date,
            image=jikan_data.get("images", {}).get("jpg", {}).get("large_image_url"),
            total_episodes=jikan_data.get("episodes"),
            studio=studio,
            status=status_map.get(
                jikan_data.get("status"), AnimeSeriesStatusEnum.FINISHED
            ),
            is_custom=False,
        )
