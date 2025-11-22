from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from core.config import settings
from models import PlatformEnum
from schemas import GameCreate

from .base import BaseAPIService, logger

logger = logger.getChild("igdb_service")


class IGDBService(BaseAPIService):
    """Service for Internet Game Database API."""

    def __init__(self):
        self._access_token = settings.IGDB_ACCESS_TOKEN

        super().__init__(
            base_url="https://api.igdb.com/v4", headers=self._build_headers()
        )

    def _build_headers(self) -> dict:
        """Build authentication headers."""
        if not settings.IGDB_CLIENT_ID or not self._access_token:
            return {}
        return {
            "Client-ID": settings.IGDB_CLIENT_ID,
            "Authorization": f"Bearer {self._access_token}",
        }

    async def _check_auth(self) -> bool:
        """Check if authenticated and obtain token if needed."""
        if self._access_token and self._is_token_valid():
            logger.debug("Using existing valid IGDB access token")
            return True

        if not settings.IGDB_CLIENT_ID or not settings.IGDB_CLIENT_SECRET:
            logger.error("IGDB_CLIENT_ID and IGDB_CLIENT_SECRET are required")
            return False

        logger.debug("Generating new IGDB access token...")

        try:
            auth_url = "https://id.twitch.tv/oauth2/token"
            params = {
                "client_id": settings.IGDB_CLIENT_ID,
                "client_secret": settings.IGDB_CLIENT_SECRET,
                "grant_type": "client_credentials",
            }

            async with self.session.post(auth_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                self._access_token = data.get("access_token")
                expires_in = data.get("expires_in")  # seconds from now

                if not self._access_token or not expires_in:
                    logger.error("Failed to obtain access token")
                    return False

                expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                # Update headers with new token
                self.headers = self._build_headers()

                # Update ENV variables in settings
                settings.IGDB_ACCESS_TOKEN = self._access_token
                settings.IGDB_TOKEN_EXPIRES_AT = expires_at.isoformat()

                # Close existing session and recreate with new headers
                if self._session and not self._session.closed:
                    await self._session.close()
                self._session = None

                # Save token to .env file
                self._save_token_to_env(self._access_token, expires_at)

                logger.debug(
                    f"Successfully generated and saved IGDB access token (expires in {expires_in}s)"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            return False

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not settings.IGDB_TOKEN_EXPIRES_AT:
            return False

        try:
            expires_at = datetime.fromisoformat(settings.IGDB_TOKEN_EXPIRES_AT)
            is_valid = datetime.now(timezone.utc) < expires_at
            if not is_valid:
                logger.debug("IGDB access token has expired")
            return is_valid
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to parse token expiration: {e}")
            return False

    def _save_token_to_env(self, token: str, expires_at: Optional[datetime] = None):
        """Save access token and expiration to .env file."""
        try:
            env_path = Path(__file__).parent.parent.parent / ".env"

            if env_path.exists():
                with open(env_path, "r") as f:
                    lines = f.readlines()

                token_exists = False
                expires_exists = False

                for i, line in enumerate(lines):
                    if line.startswith("IGDB_ACCESS_TOKEN="):
                        lines[i] = f"IGDB_ACCESS_TOKEN={token}\n"
                        token_exists = True
                    elif line.startswith("IGDB_TOKEN_EXPIRES_AT="):
                        if expires_at:
                            lines[i] = (
                                f"IGDB_TOKEN_EXPIRES_AT={expires_at.isoformat()}\n"
                            )
                        expires_exists = True

                if not token_exists:
                    lines.append(f"\nIGDB_ACCESS_TOKEN={token}\n")

                if not expires_exists and expires_at:
                    lines.append(f"IGDB_TOKEN_EXPIRES_AT={expires_at.isoformat()}\n")

                with open(env_path, "w") as f:
                    f.writelines(lines)
            else:
                with open(env_path, "w") as f:
                    f.write(f"IGDB_ACCESS_TOKEN={token}\n")
                    if expires_at:
                        f.write(f"IGDB_TOKEN_EXPIRES_AT={expires_at.isoformat()}\n")

            logger.debug(f"Saved IGDB access token to {env_path}")

        except Exception as e:
            logger.error(f"Failed to save token to .env: {e}")

    async def _query(self, endpoint: str, query: str) -> Optional[List[dict]]:
        """Execute IGDB query using Apicalypse."""
        if not await self._check_auth():
            logger.error("Not authenticated with IGDB")
            return None

        logger.debug(f"Executing IGDB query: {query[:100]}...")
        data = await self._post(endpoint, data=query)
        if isinstance(data, list):
            logger.debug(f"IGDB query returned {len(data)} results")
            return data
        logger.warning("IGDB query returned non-list response")
        return None

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search games."""
        logger.debug(f"Searching IGDB for: {query} (limit: {limit})")
        apicalypse = f'search "{query}"; fields name,summary,first_release_date,cover.url,platforms.name,themes.name,genres.name,game_modes.name,involved_companies.company.name,involved_companies.developer,involved_companies.publisher; limit {limit};'
        data = await self._query("games", apicalypse)
        results = data if data else []
        logger.debug(f"IGDB search returned {len(results)} results: {results}")
        return results

    async def get_by_id(self, media_id: str) -> Optional[dict]:
        """Get game details."""
        logger.debug(f"Fetching IGDB game by ID: {media_id}")
        apicalypse = f"fields name,summary,first_release_date,cover.url,platforms.name,themes.name,genres.name,game_modes.name,involved_companies.company.name,involved_companies.developer,involved_companies.publisher; where id = {media_id};"
        data = await self._query("games", apicalypse)
        if data and len(data) > 0:
            logger.debug(
                f"Found game: {data[0].get('name', 'Unknown')}, data: {data[0]}"
            )
            return data[0]
        logger.warning(f"Game not found with ID: {media_id}")
        return None

    def to_game_create(self, igdb_data: dict) -> GameCreate:
        """Convert IGDB data to GameCreate schema."""
        # Extract platforms
        platforms = []
        platform_map = {
            "PC (Microsoft Windows)": PlatformEnum.PC,
            "PlayStation 5": PlatformEnum.PS5,
            "PlayStation 4": PlatformEnum.PS4,
            "PlayStation 3": PlatformEnum.PS3,
            "Xbox Series X|S": PlatformEnum.XBOX_SERIES,
            "Xbox One": PlatformEnum.XBOX_ONE,
            "Nintendo Switch": PlatformEnum.SWITCH,
            "iOS": PlatformEnum.MOBILE,
            "Android": PlatformEnum.MOBILE,
        }

        for platform in igdb_data.get("platforms", []):
            platform_name = platform.get("name", "")
            mapped = platform_map.get(platform_name)
            if mapped and mapped not in platforms:
                platforms.append(mapped)

        # Extract developers and publishers
        developers = []
        publishers = []
        for company in igdb_data.get("involved_companies", []):
            company_name = company.get("company", {}).get("name")
            if company.get("developer") and company_name:
                developers.append(company_name)
            if company.get("publisher") and company_name:
                publishers.append(company_name)

        # Parse release date
        release_date = None
        if igdb_data.get("first_release_date"):
            try:
                release_date = datetime.fromtimestamp(
                    igdb_data["first_release_date"]
                ).date()
            except (ValueError, OSError, TypeError):
                pass

        # Extract tags from genres, themes, and game_modes
        tags = []
        for genre in igdb_data.get("genres", []):
            if genre.get("name"):
                tags.append(genre["name"])
        for theme in igdb_data.get("themes", []):
            if theme.get("name"):
                tags.append(theme["name"])
        for mode in igdb_data.get("game_modes", []):
            if mode.get("name"):
                tags.append(mode["name"])

        logger.debug(f"Converting IGDB data for: {igdb_data.get('name', 'Unknown')}")

        return GameCreate(
            title=igdb_data.get("name", "Unknown"),
            description=igdb_data.get("summary") or igdb_data.get("storyline"),
            release_date=release_date,
            cover_image_url=self._get_cover_url(igdb_data.get("cover")),
            external_id=str(igdb_data.get("id")),
            external_source="igdb",
            platforms=platforms,
            developers=developers if developers else None,
            publishers=publishers if publishers else None,
            tags=tags,
        )

    @staticmethod
    def _get_cover_url(cover_data: Optional[dict]) -> Optional[str]:
        """Build cover URL."""
        if not cover_data or "url" not in cover_data:
            return None
        url = cover_data["url"].replace("t_thumb", "t_cover_big")
        return f"https:{url}" if url.startswith("//") else url
