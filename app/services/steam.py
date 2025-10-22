from datetime import datetime
from typing import List, Optional

from app.core.config import settings
from app.schemas.game import GameCreate
from app.services.base import BaseAPIService


class SteamService(BaseAPIService):
    """Service for Steam Web API."""

    def __init__(self):
        super().__init__(base_url="https://api.steampowered.com", timeout=15)
        self.store_api = "https://store.steampowered.com/api"
        self.api_key = settings.STEAM_API_KEY

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search games."""
        params = {"term": query, "l": "english", "cc": "US"}
        try:
            async with self.session.get(
                f"{self.store_api}/storesearch", params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("items", [])[:limit] if data else []
        except Exception:
            return []

    async def get_details(self, app_id: str) -> Optional[dict]:
        """Get game details."""
        params = {"appids": app_id, "l": "english"}
        try:
            async with self.session.get(
                f"{self.store_api}/appdetails", params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()
                if data and app_id in data and data[app_id].get("success"):
                    return data[app_id].get("data")
        except Exception:
            pass
        return None

    def to_game_create(self, steam_data: dict) -> GameCreate:
        """Convert Steam data to GameCreate schema."""
        from app.models.game import PlatformEnum

        release_date = None
        if steam_data.get("release_date", {}).get("date"):
            try:
                date_str = steam_data["release_date"]["date"]
                release_date = datetime.strptime(date_str, "%b %d, %Y").date()
            except (ValueError, KeyError):
                pass

        developer = None
        if "developers" in steam_data and steam_data["developers"]:
            developer = steam_data["developers"][0]

        publisher = None
        if "publishers" in steam_data and steam_data["publishers"]:
            publisher = steam_data["publishers"][0]

        return GameCreate(
            title=steam_data.get("name", "Unknown"),
            description=steam_data.get("short_description"),
            release_date=release_date,
            image=steam_data.get("header_image"),
            platform=PlatformEnum.PC,
            developer=developer,
            publisher=publisher,
            steam_id=str(steam_data.get("steam_appid")),
            is_custom=False,
        )
