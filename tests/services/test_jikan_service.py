from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.schemas.anime import AnimeCreate
from app.services.jikan import JikanService


@pytest.mark.services
class TestJikanService:
    """Test Jikan service."""

    @pytest_asyncio.fixture
    async def jikan_service(self):
        """Create Jikan service instance."""
        service = JikanService()
        yield service
        await service.close()

    @pytest.fixture
    def mock_anime_data(self):
        """Mock Jikan anime data."""
        return {
            "mal_id": 5114,
            "title": "Fullmetal Alchemist: Brotherhood",
            "synopsis": "After a horrific alchemy experiment...",
            "images": {
                "jpg": {
                    "large_image_url": "https://cdn.myanimelist.net/images/anime/1223/96541l.jpg"
                }
            },
            "episodes": 64,
            "aired": {
                "from": "2009-04-05T00:00:00+00:00",
                "to": "2010-07-04T00:00:00+00:00",
            },
            "status": "Finished Airing",
            "studios": [{"mal_id": 4, "name": "Bones"}],
        }

    @pytest.mark.asyncio
    async def test_search(self, jikan_service, mock_anime_data):
        """Test searching for anime."""
        mock_response = {"data": [mock_anime_data]}

        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            results = await jikan_service.search("Fullmetal", limit=10)

            assert len(results) == 1
            assert results[0]["title"] == "Fullmetal Alchemist: Brotherhood"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_details(self, jikan_service, mock_anime_data):
        """Test getting anime details."""
        mock_response = {"data": mock_anime_data}

        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await jikan_service.get_details("5114")

            assert result["title"] == "Fullmetal Alchemist: Brotherhood"
            assert result["episodes"] == 64
            mock_get.assert_called_once()

    def test_to_anime_create(self, jikan_service, mock_anime_data):
        """Test converting Jikan data to AnimeCreate schema."""
        anime = jikan_service.to_anime_create(mock_anime_data)

        assert isinstance(anime, AnimeCreate)
        assert anime.title == "Fullmetal Alchemist: Brotherhood"
        assert anime.total_episodes == 64
        assert anime.studio == "Bones"
        assert anime.release_date == date(2009, 4, 5)
        assert anime.is_custom is False

        from app.models.media import AnimeSeriesStatusEnum

        assert anime.status == AnimeSeriesStatusEnum.FINISHED

    def test_to_anime_create_airing(self, jikan_service):
        """Test converting currently airing anime."""
        data = {
            "title": "Test Anime",
            "synopsis": "Test synopsis",
            "images": {"jpg": {"large_image_url": "https://test.jpg"}},
            "episodes": None,
            "aired": {"from": "2024-01-01T00:00:00+00:00"},
            "status": "Currently Airing",
            "studios": [{"name": "Test Studio"}],
        }

        anime = jikan_service.to_anime_create(data)

        from app.models.media import AnimeSeriesStatusEnum

        assert anime.status == AnimeSeriesStatusEnum.AIRING
        assert anime.studio == "Test Studio"

    def test_to_anime_create_announced(self, jikan_service):
        """Test converting not yet aired anime."""
        data = {
            "title": "Test Anime",
            "synopsis": "Test synopsis",
            "images": {"jpg": {"large_image_url": "https://test.jpg"}},
            "episodes": 12,
            "aired": {"from": None},
            "status": "Not yet aired",
            "studios": [],
        }

        anime = jikan_service.to_anime_create(data)

        from app.models.media import AnimeSeriesStatusEnum

        assert anime.status == AnimeSeriesStatusEnum.UPCOMING
        assert anime.studio is None
        assert anime.release_date is None

    def test_to_anime_create_no_studios(self, jikan_service):
        """Test converting anime without studios."""
        data = {
            "title": "Test Anime",
            "synopsis": "Test synopsis",
            "images": {"jpg": {"large_image_url": "https://test.jpg"}},
            "episodes": 12,
            "aired": {"from": "2024-01-01T00:00:00+00:00"},
            "status": "Finished Airing",
            "studios": [],
        }

        anime = jikan_service.to_anime_create(data)

        assert anime.studio is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self, jikan_service):
        """Test search with no results."""
        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}

            results = await jikan_service.search("nonexistent")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error(self, jikan_service):
        """Test search with API error."""
        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            results = await jikan_service.search("test")

            assert results == []

    @pytest.mark.asyncio
    async def test_get_details_not_found(self, jikan_service):
        """Test getting details for non-existent anime."""
        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await jikan_service.get_details("999999")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_details_no_data_key(self, jikan_service):
        """Test getting details with malformed response."""
        with patch.object(jikan_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"error": "Not found"}

            result = await jikan_service.get_details("999999")

            assert result is None

    def test_to_anime_create_minimal_data(self, jikan_service):
        """Test converting anime with minimal data."""
        data = {
            "title": "Test Anime",
            "synopsis": None,
            "images": {},
            "episodes": None,
            "aired": {},
            "status": "Unknown Status",
            "studios": [],
        }

        anime = jikan_service.to_anime_create(data)

        assert anime.title == "Test Anime"
        assert anime.description is None
        assert anime.total_episodes is None
        assert anime.studio is None

        from app.models.media import AnimeSeriesStatusEnum

        assert anime.status == AnimeSeriesStatusEnum.FINISHED  # Default
