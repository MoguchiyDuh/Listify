from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.schemas.book import BookCreate
from app.services.openlibrary import OpenLibraryService


@pytest.mark.services
class TestOpenLibraryService:
    """Test Open Library service."""

    @pytest_asyncio.fixture
    async def openlibrary_service(self):
        """Create Open Library service instance."""
        service = OpenLibraryService()
        yield service
        await service.close()

    @pytest.fixture
    def mock_book_data(self):
        """Mock Open Library book data."""
        return {
            "key": "/works/OL45804W",
            "title": "The Great Gatsby",
            "author_name": ["F. Scott Fitzgerald"],
            "first_publish_year": 1925,
            "isbn": ["9780743273565", "0743273567"],
            "cover_i": 12345678,
            "number_of_pages_median": 180,
        }

    @pytest.mark.asyncio
    async def test_search(self, openlibrary_service, mock_book_data):
        """Test searching for books."""
        mock_response = {"docs": [mock_book_data]}

        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_response

            results = await openlibrary_service.search("Great Gatsby", limit=10)

            assert len(results) == 1
            assert results[0]["title"] == "The Great Gatsby"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_details(self, openlibrary_service):
        """Test getting book details."""
        mock_work_data = {
            "key": "/works/OL45804W",
            "title": "The Great Gatsby",
            "description": "A classic novel...",
        }

        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_work_data

            result = await openlibrary_service.get_details("OL45804W")

            assert result["title"] == "The Great Gatsby"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_details_with_works_prefix(self, openlibrary_service):
        """Test getting details with /works/ prefix."""
        mock_work_data = {"title": "Test Book"}

        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_work_data

            result = await openlibrary_service.get_details("/works/OL45804W")

            assert result["title"] == "Test Book"
            mock_get.assert_called_once_with("works/OL45804W.json")

    @pytest.mark.asyncio
    async def test_search_by_isbn(self, openlibrary_service):
        """Test searching by ISBN."""
        mock_response = {
            "ISBN:9780743273565": {
                "title": "The Great Gatsby",
                "authors": [{"name": "F. Scott Fitzgerald"}],
            }
        }

        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_response

            result = await openlibrary_service.search_by_isbn("9780743273565")

            assert result["title"] == "The Great Gatsby"
            mock_get.assert_called_once()

    def test_to_book_create(self, openlibrary_service, mock_book_data):
        """Test converting Open Library data to BookCreate schema."""
        book = openlibrary_service.to_book_create(mock_book_data)

        assert isinstance(book, BookCreate)
        assert book.title == "The Great Gatsby"
        assert book.author == "F. Scott Fitzgerald"
        assert book.isbn == "9780743273565"
        assert book.pages == 180
        assert book.release_date == date(1925, 1, 1)
        assert book.is_custom is False
        assert "covers.openlibrary.org" in book.image

    def test_to_book_create_no_author(self, openlibrary_service):
        """Test converting book without author."""
        data = {
            "title": "Test Book",
            "first_publish_year": 2024,
            "isbn": ["1234567890"],
            "cover_i": 123,
        }

        book = openlibrary_service.to_book_create(data)

        assert book.title == "Test Book"
        assert book.author is None

    def test_to_book_create_no_isbn(self, openlibrary_service):
        """Test converting book without ISBN."""
        data = {
            "title": "Test Book",
            "author_name": ["Test Author"],
            "first_publish_year": 2024,
            "cover_i": 123,
        }

        book = openlibrary_service.to_book_create(data)

        assert book.isbn is None

    def test_to_book_create_no_cover(self, openlibrary_service):
        """Test converting book without cover."""
        data = {
            "title": "Test Book",
            "author_name": ["Test Author"],
            "first_publish_year": 2024,
            "isbn": ["1234567890"],
        }

        book = openlibrary_service.to_book_create(data)

        assert book.image is None

    def test_to_book_create_description_as_object(self, openlibrary_service):
        """Test converting book with description as object."""
        data = {
            "title": "Test Book",
            "description": {"value": "This is a description"},
            "author_name": ["Test Author"],
            "first_publish_year": 2024,
            "isbn": ["1234567890"],
            "cover_i": 123,
        }

        book = openlibrary_service.to_book_create(data)

        assert book.description is None

    def test_to_book_create_description_as_string(self, openlibrary_service):
        """Test converting book with description as string."""
        data = {
            "title": "Test Book",
            "description": "This is a description",
            "author_name": ["Test Author"],
            "first_publish_year": 2024,
            "isbn": ["1234567890"],
            "cover_i": 123,
        }

        book = openlibrary_service.to_book_create(data)

        assert book.description == "This is a description"

    def test_get_cover_url(self):
        """Test building cover URL."""
        url = OpenLibraryService.get_cover_url(12345678)
        assert url == "https://covers.openlibrary.org/b/id/12345678-L.jpg"

        url = OpenLibraryService.get_cover_url(None)
        assert url is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self, openlibrary_service):
        """Test search with no results."""
        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"docs": []}

            results = await openlibrary_service.search("nonexistent")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error(self, openlibrary_service):
        """Test search with API error."""
        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            results = await openlibrary_service.search("test")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_by_isbn_not_found(self, openlibrary_service):
        """Test searching by ISBN with no results."""
        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {}

            result = await openlibrary_service.search_by_isbn("9999999999")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_details_not_found(self, openlibrary_service):
        """Test getting details for non-existent book."""
        with patch.object(
            openlibrary_service, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            result = await openlibrary_service.get_details("OL999999W")

            assert result is None

    def test_to_book_create_invalid_year(self, openlibrary_service):
        """Test converting book with invalid year."""
        data = {
            "title": "Test Book",
            "author_name": ["Test Author"],
            "first_publish_year": 999999,
            "isbn": ["1234567890"],
            "cover_i": 123,
        }

        book = openlibrary_service.to_book_create(data)

        assert book.release_date is None
