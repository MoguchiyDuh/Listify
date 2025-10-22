from datetime import datetime
from typing import List, Optional

from app.schemas.book import BookCreate
from app.services.base import BaseAPIService


class OpenLibraryService(BaseAPIService):
    """Service for Open Library API."""

    def __init__(self):
        super().__init__(base_url="https://openlibrary.org", timeout=15)

    async def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search books."""
        params = {
            "q": query,
            "limit": limit,
            "fields": "key,title,author_name,first_publish_year,isbn,cover_i,number_of_pages_median",
        }
        data = await self._get("search.json", params)
        return data.get("docs", []) if data else []

    async def get_details(self, work_id: str) -> Optional[dict]:
        """Get book work details."""
        work_id = work_id.replace("/works/", "")
        return await self._get(f"works/{work_id}.json")

    async def search_by_isbn(self, isbn: str) -> Optional[dict]:
        """Search by ISBN."""
        params = {"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"}
        data = await self._get("api/books", params)
        return data.get(f"ISBN:{isbn}") if data else None

    def to_book_create(self, ol_data: dict) -> BookCreate:
        """Convert Open Library data to BookCreate schema."""
        author = None
        if "author_name" in ol_data and ol_data["author_name"]:
            author = ol_data["author_name"][0]

        isbn = None
        if "isbn" in ol_data and ol_data["isbn"]:
            isbn = ol_data["isbn"][0]

        release_date = None
        if ol_data.get("first_publish_year"):
            try:
                release_date = datetime(ol_data["first_publish_year"], 1, 1).date()
            except (ValueError, TypeError):
                pass

        return BookCreate(
            title=ol_data.get("title", "Unknown"),
            description=(
                ol_data.get("description")
                if isinstance(ol_data.get("description"), str)
                else None
            ),
            release_date=release_date,
            image=self.get_cover_url(ol_data.get("cover_i")),
            pages=ol_data.get("number_of_pages_median"),
            author=author,
            isbn=isbn,
            is_custom=False,
        )

    @staticmethod
    def get_cover_url(cover_id: Optional[int]) -> Optional[str]:
        """Build cover URL."""
        return (
            f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            if cover_id
            else None
        )
