from datetime import datetime
from typing import List, Optional

from schemas import BookCreate

from .base import BaseAPIService, logger

logger = logger.getChild("openlibrary")


class OpenLibraryService(BaseAPIService):
    """Service for Open Library API."""

    def __init__(self):
        super().__init__(base_url="https://openlibrary.org", timeout=15)

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search books."""
        logger.debug(f"Searching Open Library for: {query} (limit: {limit})")
        params = {
            "q": query,
            "limit": limit,
            "fields": "key,title,author_name,first_publish_year,isbn,cover_i,number_of_pages_median,subject_key",
            "sort": "currently_reading",
        }
        data = await self._get("search.json", params)
        results = data.get("docs", []) if data else []
        logger.debug(f"Open Library search returned {len(results)} results: {results}")
        return results

    async def get_by_id(self, media_id: str) -> Optional[dict]:
        """Get book work details."""
        logger.debug(f"Fetching Open Library book by ID: {media_id}")
        media_id = media_id.replace("/works/", "").lstrip("/")
        data = await self._get(f"works/{media_id}.json")
        if data:
            logger.debug(f"Found book: {data.get('title', 'Unknown')}, data: {data}")
        else:
            logger.warning(f"Book not found with ID: {media_id}")
        return data

    async def search_by_isbn(self, isbn: str) -> Optional[dict]:
        """Search by ISBN."""
        logger.debug(f"Searching Open Library by ISBN: {isbn}")
        params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        data = await self._get("api/books", params)
        result = data.get(f"ISBN:{isbn}") if data else None
        if result:
            logger.debug(
                f"Found book by ISBN: {result.get('title', 'Unknown')}, data: {result}"
            )
        else:
            logger.warning(f"Book not found with ISBN: {isbn}")
        return result

    def to_book_create(self, ol_data: dict) -> BookCreate:
        """Convert Open Library data to BookCreate schema."""
        # Extract author
        author = None
        if "author_name" in ol_data and ol_data["author_name"]:
            author = ol_data["author_name"][0]

        # Extract ISBN
        isbn = None
        if "isbn" in ol_data and ol_data["isbn"]:
            isbn = ol_data["isbn"][0]

        # Parse release date
        release_date = None
        if ol_data.get("first_publish_year"):
            try:
                release_date = datetime(ol_data["first_publish_year"], 1, 1).date()
            except (ValueError, TypeError):
                pass

        # Handle description (can be string or dict)
        description = ol_data.get("description")
        if isinstance(description, dict):
            description = description.get("value")

        # Extract tags from subject_keys
        tags = []
        if ol_data.get("subject_key"):
            tags = [subject_key_name for subject_key_name in ol_data["subject_key"]]

        logger.debug(
            f"Converting Open Library data for: {ol_data.get('title', 'Unknown')}"
        )

        return BookCreate(
            title=ol_data.get("title", "Unknown"),
            description=description,
            release_date=release_date,
            cover_image_url=self.get_cover_url(ol_data.get("cover_i")),
            external_id=ol_data.get("key", "").split("/")[-1],
            external_source="openlibrary",
            pages=ol_data.get("number_of_pages_median"),
            author=author,
            isbn=isbn,
            tags=tags if tags else None,
        )

    @staticmethod
    def get_cover_url(cover_id: Optional[int]) -> Optional[str]:
        """Build cover URL."""
        return (
            f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            if cover_id
            else None
        )
