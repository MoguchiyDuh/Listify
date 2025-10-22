from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.schemas.game import GameCreate
from app.services.igdb import IGDBService


@pytest.mark.services
class TestIGDBService:
    """Test IGDB service."""

    @pytest_asyncio.fixture
    async def igdb_service(self):
        """Create IGDB service instance."""
        service = IGDBService()
        yield service
        await service.close()

    @pytest.fixture
    def mock_game_data(self):
        """Mock IGDB game data."""
        return {
            "id": 1942,
            "name": "The Witcher 3: Wild Hunt",
            "summary": "As war rages on...",
            "cover": {
                "id": 89386,
                "url": "//images.igdb.com/igdb/image/upload/t_thumb/co1wyy.jpg",
            },
            "first_release_date": 1431993600,
            "platforms": [
                {"id": 6, "name": "PC (Microsoft Windows)"},
                {"id": 48, "name": "PlayStation 4"},
            ],
            "involved_companies": [
                {
                    "company": {"id": 908, "name": "CD Projekt RED"},
                    "developer": True,
                    "publisher": False,
                },
                {
                    "company": {"id": 908, "name": "CD Projekt RED"},
                    "developer": False,
                    "publisher": True,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_search(self, igdb_service, mock_game_data):
        """Test searching for games."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [mock_game_data]

            results = await igdb_service.search("Witcher", limit=10)

            assert len(results) == 1
            assert results[0]["name"] == "The Witcher 3: Wild Hunt"
            mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_details(self, igdb_service, mock_game_data):
        """Test getting game details."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [mock_game_data]

            result = await igdb_service.get_details("1942")

            assert result["name"] == "The Witcher 3: Wild Hunt"
            mock_query.assert_called_once()

    def test_to_game_create(self, igdb_service, mock_game_data):
        """Test converting IGDB data to GameCreate schema."""
        game = igdb_service.to_game_create(mock_game_data)

        assert isinstance(game, GameCreate)
        assert game.title == "The Witcher 3: Wild Hunt"
        assert game.developer == "CD Projekt RED"
        assert game.publisher == "CD Projekt RED"
        assert game.release_date == date(2015, 5, 19)
        assert game.is_custom is False

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.PC

    def test_to_game_create_playstation_platform(self, igdb_service):
        """Test converting game with PlayStation platform."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "platforms": [{"name": "PlayStation 5"}],
            "involved_companies": [
                {"company": {"name": "Test Dev"}, "developer": True, "publisher": False}
            ],
        }

        game = igdb_service.to_game_create(data)

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.PLAYSTATION

    def test_to_game_create_xbox_platform(self, igdb_service):
        """Test converting game with Xbox platform."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "platforms": [{"name": "Xbox Series X|S"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.XBOX

    def test_to_game_create_nintendo_platform(self, igdb_service):
        """Test converting game with Nintendo platform."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "platforms": [{"name": "Nintendo Switch"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.NINTENDO

    def test_to_game_create_mobile_platform(self, igdb_service):
        """Test converting game with mobile platform."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "platforms": [{"name": "Android"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.OTHER

    def test_to_game_create_no_platforms(self, igdb_service):
        """Test converting game without platforms."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.OTHER

    def test_to_game_create_no_companies(self, igdb_service):
        """Test converting game without companies."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "first_release_date": 1431993600,
            "platforms": [{"name": "PC"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        assert game.developer is None
        assert game.publisher is None

    def test_to_game_create_no_cover(self, igdb_service):
        """Test converting game without cover."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "first_release_date": 1431993600,
            "platforms": [{"name": "PC"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        assert game.image is None

    def test_to_game_create_no_release_date(self, igdb_service):
        """Test converting game without release date."""
        data = {
            "name": "Test Game",
            "summary": "Test summary",
            "cover": {"url": "//test.jpg"},
            "platforms": [{"name": "PC"}],
            "involved_companies": [],
        }

        game = igdb_service.to_game_create(data)

        assert game.release_date is None

    def test_get_cover_url(self):
        """Test building cover URL."""
        cover = {"url": "//images.igdb.com/igdb/image/upload/t_thumb/co1wyy.jpg"}
        url = IGDBService.get_cover_url(cover)
        assert url == "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg"

        url = IGDBService.get_cover_url(None)
        assert url is None

        url = IGDBService.get_cover_url({})
        assert url is None

    def test_get_cover_url_already_https(self):
        """Test building cover URL when already HTTPS."""
        cover = {"url": "https://images.igdb.com/igdb/image/upload/t_thumb/co1wyy.jpg"}
        url = IGDBService.get_cover_url(cover)
        assert url.startswith("https://")
        assert "t_cover_big" in url

    @pytest.mark.asyncio
    async def test_search_empty_results(self, igdb_service):
        """Test search with no results."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            results = await igdb_service.search("nonexistent")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error(self, igdb_service):
        """Test search with API error."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = None

            results = await igdb_service.search("test")

            assert results == []

    @pytest.mark.asyncio
    async def test_get_details_not_found(self, igdb_service):
        """Test getting details for non-existent game."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = []

            result = await igdb_service.get_details("999999")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_details_api_error(self, igdb_service):
        """Test getting details with API error."""
        with patch.object(igdb_service, "_query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = None

            result = await igdb_service.get_details("1942")

            assert result is None

    def test_build_headers(self, igdb_service):
        """Test building authentication headers."""
        headers = igdb_service._build_headers()

        assert "Client-ID" in headers
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
