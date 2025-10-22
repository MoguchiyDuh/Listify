from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.schemas.game import GameCreate
from app.services.steam import SteamService


@pytest.mark.services
class TestSteamService:
    """Test Steam service."""

    @pytest_asyncio.fixture
    async def steam_service(self):
        """Create Steam service instance."""
        service = SteamService()
        yield service
        await service.close()

    @pytest.fixture
    def mock_game_data(self):
        """Mock Steam game data."""
        return {
            "steam_appid": 292030,
            "name": "The Witcher 3: Wild Hunt",
            "short_description": "As war rages on throughout the Northern Realms...",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg",
            "release_date": {"date": "May 18, 2015"},
            "developers": ["CD PROJEKT RED"],
            "publishers": ["CD PROJEKT RED"],
        }

    @pytest.mark.asyncio
    async def test_search(self, steam_service):
        """Test searching for games."""
        mock_response = {
            "items": [
                {"id": 292030, "name": "The Witcher 3: Wild Hunt"},
                {"id": 1174180, "name": "Red Dead Redemption 2"},
            ]
        }

        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock()
        mock_session_response.json = AsyncMock(return_value=mock_response)
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            results = await steam_service.search("witcher", limit=10)

            assert len(results) == 2
            assert results[0]["name"] == "The Witcher 3: Wild Hunt"

    @pytest.mark.asyncio
    async def test_get_details(self, steam_service, mock_game_data):
        """Test getting game details."""
        mock_response = {
            "292030": {
                "success": True,
                "data": mock_game_data,
            }
        }

        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock()
        mock_session_response.json = AsyncMock(return_value=mock_response)
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            result = await steam_service.get_details("292030")

            assert result["name"] == "The Witcher 3: Wild Hunt"
            assert result["steam_appid"] == 292030

    def test_to_game_create(self, steam_service, mock_game_data):
        """Test converting Steam data to GameCreate schema."""
        game = steam_service.to_game_create(mock_game_data)

        assert isinstance(game, GameCreate)
        assert game.title == "The Witcher 3: Wild Hunt"
        assert game.developer == "CD PROJEKT RED"
        assert game.publisher == "CD PROJEKT RED"
        assert game.release_date == date(2015, 5, 18)
        assert game.steam_id == "292030"
        assert game.is_custom is False

        from app.models.game import PlatformEnum

        assert game.platform == PlatformEnum.PC

    def test_to_game_create_no_developers(self, steam_service):
        """Test converting game without developers."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
            "short_description": "Test description",
            "header_image": "https://test.jpg",
            "release_date": {"date": "Jan 1, 2024"},
            "publishers": ["Test Publisher"],
        }

        game = steam_service.to_game_create(data)

        assert game.developer is None
        assert game.publisher == "Test Publisher"

    def test_to_game_create_no_publishers(self, steam_service):
        """Test converting game without publishers."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
            "short_description": "Test description",
            "header_image": "https://test.jpg",
            "release_date": {"date": "Jan 1, 2024"},
            "developers": ["Test Developer"],
        }

        game = steam_service.to_game_create(data)

        assert game.developer == "Test Developer"
        assert game.publisher is None

    def test_to_game_create_invalid_date(self, steam_service):
        """Test converting game with invalid date format."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
            "short_description": "Test description",
            "header_image": "https://test.jpg",
            "release_date": {"date": "Coming Soon"},
            "developers": ["Test Developer"],
            "publishers": ["Test Publisher"],
        }

        game = steam_service.to_game_create(data)

        assert game.release_date is None

    def test_to_game_create_no_release_date(self, steam_service):
        """Test converting game without release date."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
            "short_description": "Test description",
            "header_image": "https://test.jpg",
            "developers": ["Test Developer"],
            "publishers": ["Test Publisher"],
        }

        game = steam_service.to_game_create(data)

        assert game.release_date is None

    def test_to_game_create_minimal_data(self, steam_service):
        """Test converting game with minimal data."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
        }

        game = steam_service.to_game_create(data)

        assert game.title == "Test Game"
        assert game.steam_id == "12345"
        assert game.description is None
        assert game.developer is None
        assert game.publisher is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self, steam_service):
        """Test search with no results."""
        mock_response = {"items": []}

        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock()
        mock_session_response.json = AsyncMock(return_value=mock_response)
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            results = await steam_service.search("nonexistent")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error(self, steam_service):
        """Test search with API error."""
        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock(
            side_effect=Exception("API Error")
        )
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock(return_value=None)

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            results = await steam_service.search("test")

            assert results == []

    @pytest.mark.asyncio
    async def test_get_details_not_found(self, steam_service):
        """Test getting details for non-existent game."""
        mock_response = {
            "999999": {
                "success": False,
            }
        }

        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock()
        mock_session_response.json = AsyncMock(return_value=mock_response)
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            result = await steam_service.get_details("999999")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_details_api_error(self, steam_service):
        """Test getting details with API error."""
        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock(
            side_effect=Exception("API Error")
        )
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            result = await steam_service.get_details("292030")

            assert result is None

    @pytest.mark.asyncio
    async def test_search_with_limit(self, steam_service):
        """Test search with limit parameter."""
        mock_response = {"items": [{"id": i, "name": f"Game {i}"} for i in range(20)]}

        mock_session_response = AsyncMock()
        mock_session_response.raise_for_status = MagicMock()
        mock_session_response.json = AsyncMock(return_value=mock_response)
        mock_session_response.__aenter__ = AsyncMock(return_value=mock_session_response)
        mock_session_response.__aexit__ = AsyncMock()

        with patch.object(
            steam_service.session, "get", return_value=mock_session_response
        ):
            results = await steam_service.search("test", limit=5)

            assert len(results) == 5

    def test_to_game_create_different_date_format(self, steam_service):
        """Test converting game with different date format."""
        data = {
            "steam_appid": 12345,
            "name": "Test Game",
            "short_description": "Test description",
            "header_image": "https://test.jpg",
            "release_date": {"date": "Dec 31, 2024"},
            "developers": ["Test Developer"],
            "publishers": ["Test Publisher"],
        }

        game = steam_service.to_game_create(data)

        assert game.release_date == date(2024, 12, 31)
