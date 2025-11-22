from unittest.mock import AsyncMock, patch

import pytest

from services.openlibrary import OpenLibraryService


@pytest.mark.services
class TestOpenLibraryService:
    """Test OpenLibrary service with mocked responses"""

    @pytest.mark.asyncio
    async def test_search_books(self, load_fixture):
        """Test book search with mocked response"""
        fixture_data = load_fixture("openlibrary", "book_search.json")

        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"docs": fixture_data}

            async with OpenLibraryService() as service:
                results = await service.search("Dune", limit=3)

                assert results == fixture_data
                assert len(results) == 3
                assert results[0]["key"] is not None
                assert results[0]["title"] is not None

    @pytest.mark.asyncio
    async def test_get_by_id(self, load_fixture):
        """Test getting book by work ID with mocked response"""
        fixture_data = load_fixture("openlibrary", "book_details.json")

        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = [fixture_data, {"name": "Frank Herbert"}]

            async with OpenLibraryService() as service:
                book = await service.get_by_id("/works/OL893415W")

                assert book is not None
                assert "Dune" in book["title"]
                assert book["author_name"] == ["Frank Herbert"]

    @pytest.mark.asyncio
    async def test_get_by_id_stripped(self, load_fixture):
        """Test getting book with stripped work ID"""
        fixture_data = load_fixture("openlibrary", "book_details.json")

        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = [fixture_data, {"name": "Frank Herbert"}]

            async with OpenLibraryService() as service:
                book = await service.get_by_id("OL893415W")

                assert book is not None
                assert book["author_name"] == ["Frank Herbert"]
                assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_get_by_invalid_id(self):
        """Test getting book with invalid ID"""
        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = None

            async with OpenLibraryService() as service:
                book = await service.get_by_id("INVALID123")
                assert book is None

    @pytest.mark.asyncio
    async def test_search_by_isbn(self, load_fixture):
        """Test searching by ISBN with mocked response"""
        fixture_data = load_fixture("openlibrary", "isbn_search.json")

        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"ISBN:9780441013593": fixture_data}

            async with OpenLibraryService() as service:
                book = await service.search_by_isbn("9780441013593")

                assert book is not None
                assert book["title"] == "Dune"

    @pytest.mark.asyncio
    async def test_search_by_invalid_isbn(self):
        """Test searching by invalid ISBN"""
        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {}

            async with OpenLibraryService() as service:
                book = await service.search_by_isbn("0000000000000")
                assert book is None

    @pytest.mark.asyncio
    async def test_to_book_create(self, load_fixture):
        """Test converting OpenLibrary data to BookCreate schema"""
        fixture_data = load_fixture("openlibrary", "book_search.json")
        service = OpenLibraryService()

        book_create = service.to_book_create(fixture_data[0])

        assert book_create.title is not None
        assert book_create.external_source == "openlibrary"
        assert book_create.external_id is not None
        assert book_create.authors is not None

        await service.close()

    @pytest.mark.asyncio
    async def test_to_book_create_with_full_data(self, load_fixture):
        """Test conversion with all available fields"""
        fixture_data = load_fixture("openlibrary", "book_search.json")
        service = OpenLibraryService()

        first = fixture_data[0]
        book_create = service.to_book_create(first)

        assert book_create.title is not None
        assert book_create.external_source == "openlibrary"

        if first.get("isbn"):
            assert book_create.isbn == first["isbn"][0]

        if first.get("first_publish_year"):
            assert book_create.release_date is not None

        if first.get("cover_i"):
            assert book_create.cover_image_url is not None
            assert book_create.cover_image_url.startswith("https://")

        if first.get("subject_key"):
            assert book_create.tags is not None
            assert len(book_create.tags) > 0

        await service.close()

    @pytest.mark.asyncio
    async def test_get_cover_url(self):
        """Test cover URL building"""
        url = OpenLibraryService.get_cover_url(12345)
        assert url == "https://covers.openlibrary.org/b/id/12345-L.jpg"

        url = OpenLibraryService.get_cover_url(None)
        assert url is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no results"""
        with patch.object(
            OpenLibraryService, "_get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"docs": []}

            async with OpenLibraryService() as service:
                results = await service.search("xyzinvalid", limit=5)
                assert results == []

    @pytest.mark.asyncio
    async def test_timeout_setting(self):
        """Test that OpenLibrary has longer timeout"""
        service = OpenLibraryService()
        assert service.timeout.total == 15
        await service.close()
