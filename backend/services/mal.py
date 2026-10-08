from typing import Any, List, Literal, Optional

from core.config import settings

from .base import logger
from .jikan import JikanService

logger = logger.bind(module="mal")

MediaKind = Literal["anime", "manga"]

ANIME_FIELDS = "id,title,alternative_titles,synopsis,main_picture,num_episodes,start_date,status,rating,genres,studios"
MANGA_FIELDS = "id,title,alternative_titles,synopsis,main_picture,num_chapters,num_volumes,start_date,status,genres,authors{first_name,last_name}"

ANIME_STATUS = {
    "finished_airing": "Finished Airing",
    "currently_airing": "Currently Airing",
    "not_yet_aired": "Not yet aired",
}
MANGA_STATUS = {
    "finished": "Finished",
    "currently_publishing": "Publishing",
    "on_hiatus": "On Hiatus",
    "discontinued": "Discontinued",
    "not_yet_published": "Not yet published",
}
RATING = {
    "g": "G - All Ages",
    "pg": "PG - Children",
    "pg_13": "PG-13 - Teens 13 or older",
    "r": "R - 17+ (violence & profanity)",
    "r+": "R+ - Mild Nudity",
    "rx": "Rx - Hentai",
}


def _full_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    parts = value.split("-")
    parts += ["01"] * (3 - len(parts))
    return "-".join(parts[:3])


def _normalize(node: dict[str, Any], kind: MediaKind) -> dict[str, Any]:
    picture = node.get("main_picture") or {}
    cover = picture.get("large") or picture.get("medium")
    alt = node.get("alternative_titles") or {}
    start = _full_date(node.get("start_date"))
    out: dict[str, Any] = {
        "mal_id": node.get("id"),
        "title": node.get("title"),
        "title_english": alt.get("en") or None,
        "title_japanese": alt.get("ja") or None,
        "synopsis": node.get("synopsis"),
        "images": {"jpg": {"image_url": picture.get("medium"), "large_image_url": cover}},
        "genres": [{"name": g["name"]} for g in node.get("genres") or [] if g.get("name")],
    }
    if kind == "anime":
        out |= {
            "episodes": node.get("num_episodes") or None,
            "status": ANIME_STATUS.get(node.get("status", "")),
            "rating": RATING.get(node.get("rating", "")),
            "studios": [{"name": s["name"]} for s in node.get("studios") or [] if s.get("name")],
            "aired": {"from": start},
        }
    else:
        authors = []
        for a in node.get("authors") or []:
            person = a.get("node") or {}
            name = ", ".join(p for p in (person.get("last_name"), person.get("first_name")) if p)
            if name:
                authors.append({"name": name})
        out |= {
            "chapters": node.get("num_chapters") or None,
            "volumes": node.get("num_volumes") or None,
            "status": MANGA_STATUS.get(node.get("status", "")),
            "authors": authors,
            "published": {"from": start},
        }
    return out


class MALService(JikanService):
    SOURCE = "mal"

    def __init__(self):
        if not settings.MAL_CLIENT_ID:
            logger.warning("MAL_CLIENT_ID is not set, anime/manga search will fail")
        super(JikanService, self).__init__(
            base_url="https://api.myanimelist.net/v2",
            headers={"X-MAL-CLIENT-ID": settings.MAL_CLIENT_ID or ""},
            cache_source="mal",
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        media_type: MediaKind = "anime",
    ) -> List[dict]:
        query = query.strip()
        if len(query) < 3:
            return []
        params = {
            "q": query[:64],
            "limit": min(limit, 100),
            "nsfw": "true",
            "fields": ANIME_FIELDS if media_type == "anime" else MANGA_FIELDS,
        }
        data = await self._get(media_type, params, cache_ttl=3600)
        results = [_normalize(item["node"], media_type) for item in (data or {}).get("data", []) if item.get("node")]
        logger.debug(f"MAL {media_type} search '{query}' returned {len(results)} results")
        return results

    async def get_by_id(
        self,
        media_id: str,
        media_type: MediaKind = "anime",
    ) -> Optional[dict]:
        if not str(media_id).isdigit():
            return None
        params = {"fields": ANIME_FIELDS if media_type == "anime" else MANGA_FIELDS}
        data = await self._get(f"{media_type}/{media_id}", params, cache_ttl=86400)
        if not data or "id" not in data:
            logger.warning(f"MAL {media_type} not found: {media_id}")
            return None
        return _normalize(data, media_type)
