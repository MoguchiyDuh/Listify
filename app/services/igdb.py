from datetime import datetime
from typing import List, Optional

from app.core.config import settings
from app.schemas.game import GameCreate
from app.services.base import BaseAPIService


class IGDBService(BaseAPIService):
    """Service for Internet Game Database API."""

    def __init__(self):
        super().__init__(base_url="https://api.igdb.com/v4", timeout=15)
        self.client_id = settings.IGDB_CLIENT_ID
        self.access_token = settings.IGDB_ACCESS_TOKEN

    def _build_headers(self) -> dict:
        """Build auth headers."""
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    async def _query(self, endpoint: str, query: str) -> Optional[List[dict]]:
        """Execute IGDB query."""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.post(
                url, data=query, headers=self._build_headers()
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception:
            return None

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search games."""
        apicalypse = f'search "{query}"; fields name,cover.url,first_release_date,summary,platforms.name,involved_companies.company.name,involved_companies.developer,involved_companies.publisher; limit {limit};'
        data = await self._query("games", apicalypse)
        return data if data else []

    async def get_details(self, game_id: str) -> Optional[dict]:
        """Get game details."""
        apicalypse = f"fields name,cover.url,first_release_date,summary,storyline,platforms.name,involved_companies.company.name,involved_companies.developer,involved_companies.publisher; where id = {game_id};"
        data = await self._query("games", apicalypse)
        return data[0] if data and len(data) > 0 else None

    def to_game_create(self, igdb_data: dict) -> GameCreate:
        """Convert IGDB data to GameCreate schema."""
        from app.models.game import PlatformEnum

        platform = PlatformEnum.OTHER
        if "platforms" in igdb_data and igdb_data["platforms"]:
            platform_name = igdb_data["platforms"][0].get("name", "").lower()
            platform_map = {
                "pc": PlatformEnum.PC,
                "playstation": PlatformEnum.PLAYSTATION,
                "xbox": PlatformEnum.XBOX,
                "nintendo": PlatformEnum.NINTENDO,
                "mobile": PlatformEnum.MOBILE,
            }
            for key, value in platform_map.items():
                if key in platform_name:
                    platform = value
                    break

        developer = None
        publisher = None
        if "involved_companies" in igdb_data:
            for company in igdb_data["involved_companies"]:
                if company.get("developer") and not developer:
                    developer = company.get("company", {}).get("name")
                if company.get("publisher") and not publisher:
                    publisher = company.get("company", {}).get("name")

        release_date = None
        if igdb_data.get("first_release_date"):
            release_date = datetime.fromtimestamp(
                igdb_data["first_release_date"]
            ).date()

        return GameCreate(
            title=igdb_data.get("name", "Unknown"),
            description=igdb_data.get("summary"),
            release_date=release_date,
            image=self.get_cover_url(igdb_data.get("cover")),
            platform=platform,
            developer=developer,
            publisher=publisher,
            steam_id=None,
            is_custom=False,
        )

    @staticmethod
    def get_cover_url(cover_data: Optional[dict]) -> Optional[str]:
        """Build cover URL."""
        if not cover_data or "url" not in cover_data:
            return None
        url = cover_data["url"].replace("t_thumb", "t_cover_big")
        return f"https:{url}" if url.startswith("//") else url
