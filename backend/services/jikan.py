from datetime import datetime
from typing import List, Literal, Optional

from core.cache import cached
from models import AgeRatingEnum, MediaStatusEnum
from schemas import AnimeCreate, MangaCreate

from .base import BaseAPIService, logger

logger = logger.bind(module="jikan")


class JikanService(BaseAPIService):
    """Service for Jikan API (MyAnimeList unofficial API)."""

    def __init__(self):
        super().__init__(base_url="https://api.jikan.moe/v4", cache_source="jikan")

    @cached("jikan:search", ttl=3600)
    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: Literal["anime", "manga"] = "anime",
    ) -> List[dict]:
        """Search anime or manga."""
        logger.debug(f"Searching Jikan {media_type} for: {query} (limit: {limit})")
        params = {"q": query, "limit": limit, "sfw": "false"}
        data = await self._get(media_type, params, cache_ttl=3600)
        results = data.get("data", []) if data else []
        logger.debug(f"Jikan search returned {len(results)} results")
        return results

    @cached("jikan:details", ttl=7200)
    async def get_by_id(
        self,
        media_id: str,
        media_type: Literal["anime", "manga"] = "anime",
    ) -> Optional[dict]:
        """Get anime or manga details."""
        logger.debug(f"Fetching Jikan {media_type} by ID: {media_id}")
        data = await self._get(f"{media_type}/{media_id}/full", cache_ttl=86400)
        if data and data.get("data"):
            logger.debug(
                f"Found {media_type}: {data['data'].get('title', 'Unknown')}, data: {data['data']}"
            )
            return data.get("data")
        logger.warning(f"{media_type.capitalize()} not found with ID: {media_id}")
        return None

    def to_anime_create(self, jikan_data: dict) -> AnimeCreate:
        """Convert Jikan data to AnimeCreate schema."""
        status_map = {
            "Finished Airing": MediaStatusEnum.FINISHED,
            "Currently Airing": MediaStatusEnum.AIRING,
            "Not yet aired": MediaStatusEnum.UPCOMING,
        }

        studios = []
        if "studios" in jikan_data and jikan_data["studios"]:
            studios = [s.get("name") for s in jikan_data["studios"] if s.get("name")]

        aired = jikan_data.get("aired", {})
        release_date = None
        if aired.get("from"):
            try:
                release_date = datetime.fromisoformat(
                    aired["from"].replace("Z", "+00:00")
                ).date()
            except (ValueError, AttributeError):
                pass

        tags = []
        for genre in jikan_data.get("genres", []):
            if genre.get("name"):
                tags.append(genre["name"])
        for theme in jikan_data.get("themes", []):
            if theme.get("name"):
                tags.append(theme["name"])
        for demo in jikan_data.get("demographics", []):
            if demo.get("name"):
                tags.append(demo["name"])

        age_rating_map = {
            "G - All Ages": AgeRatingEnum.G,
            "PG - Children": AgeRatingEnum.PG,
            "PG-13 - Teens 13 or older": AgeRatingEnum.PG_13,
            "R - 17+ (violence & profanity)": AgeRatingEnum.R,
            "R+ - Mild Nudity": AgeRatingEnum.R_PLUS,
            "Rx - Hentai": AgeRatingEnum.RX,
        }
        age_rating = age_rating_map.get(jikan_data.get("rating"), AgeRatingEnum.UNKNOWN)

        logger.debug(f"Converting Jikan data for: {jikan_data.get('title', 'Unknown')}")

        return AnimeCreate(
            title=jikan_data.get("title", "Unknown"),
            original_title=jikan_data.get("title_japanese"),
            description=jikan_data.get("synopsis"),
            release_date=release_date,
            cover_image_url=jikan_data.get("images", {})
            .get("jpg", {})
            .get("large_image_url"),
            external_id=str(jikan_data.get("mal_id")),
            external_source="jikan",
            total_episodes=jikan_data.get("episodes"),
            studios=studios if studios else None,
            status=status_map.get(jikan_data.get("status"), MediaStatusEnum.FINISHED),
            age_rating=age_rating,
            tags=tags,
        )

    def to_manga_create(self, jikan_data: dict) -> MangaCreate:
        """Convert Jikan manga data to MangaCreate schema."""
        status_map = {
            "Finished": MediaStatusEnum.FINISHED,
            "Publishing": MediaStatusEnum.AIRING,
            "On Hiatus": MediaStatusEnum.AIRING,
            "Discontinued": MediaStatusEnum.CANCELLED,
            "Not yet published": MediaStatusEnum.UPCOMING,
        }

        authors = []
        if "authors" in jikan_data and jikan_data["authors"]:
            authors = [a.get("name") for a in jikan_data["authors"] if a.get("name")]

        published = jikan_data.get("published", {})
        release_date = None
        if published.get("from"):
            try:
                release_date = datetime.fromisoformat(
                    published["from"].replace("Z", "+00:00")
                ).date()
            except (ValueError, AttributeError):
                pass

        tags = []
        for genre in jikan_data.get("genres", []):
            if genre.get("name"):
                tags.append(genre["name"])
        for theme in jikan_data.get("themes", []):
            if theme.get("name"):
                tags.append(theme["name"])
        for demo in jikan_data.get("demographics", []):
            if demo.get("name"):
                tags.append(demo["name"])

        logger.debug(
            f"Converting Jikan manga data for: {jikan_data.get('title', 'Unknown')}"
        )

        return MangaCreate(
            title=jikan_data.get("title", "Unknown"),
            original_title=jikan_data.get("title_japanese"),
            description=jikan_data.get("synopsis"),
            release_date=release_date,
            cover_image_url=jikan_data.get("images", {})
            .get("jpg", {})
            .get("large_image_url"),
            external_id=str(jikan_data.get("mal_id")),
            external_source="jikan",
            total_chapters=jikan_data.get("chapters"),
            total_volumes=jikan_data.get("volumes"),
            authors=authors if authors else None,
            status=status_map.get(jikan_data.get("status"), MediaStatusEnum.FINISHED),
            tags=tags,
        )
