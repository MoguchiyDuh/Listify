from unittest.mock import AsyncMock, patch

import pytest

from services.igdb import IGDBService


@pytest.mark.services
class TestIGDBService:
    """Test IGDB service with mocked responses"""

    @pytest.mark.asyncio
    async def test_search_games(self, load_fixture):
        """Test game search with mocked response"""
        fixture_data = load_fixture("igdb", "game_search.json")

        with patch.object(
            IGDBService, "_check_auth", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            with patch.object(
                IGDBService, "_post", new_callable=AsyncMock
            ) as mock_post:
                mock_post.return_value = fixture_data

                async with IGDBService() as service:
                    results = await service.search("The Witcher 3", limit=3)

                    assert results == fixture_data
                    assert len(results) == 3
                    assert results[0]["id"] == 1942
                    assert "Witcher" in results[0]["name"]

    @pytest.mark.asyncio
    async def test_get_game_by_id(self, load_fixture):
        """Test getting game by ID with mocked response"""
        fixture_data = load_fixture("igdb", "game_details.json")

        with patch.object(
            IGDBService, "_check_auth", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            with patch.object(
                IGDBService, "_post", new_callable=AsyncMock
            ) as mock_post:
                mock_post.return_value = [fixture_data]

                async with IGDBService() as service:
                    game = await service.get_by_id("1942")

                    assert game == fixture_data
                    assert game["id"] == 1942
                    assert "Witcher" in game["name"]

    @pytest.mark.asyncio
    async def test_get_by_invalid_id(self):
        """Test getting game with invalid ID"""
        with patch.object(
            IGDBService, "_check_auth", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            with patch.object(
                IGDBService, "_post", new_callable=AsyncMock
            ) as mock_post:
                mock_post.return_value = []

                async with IGDBService() as service:
                    game = await service.get_by_id("99999999")
                    assert game is None

    @pytest.mark.asyncio
    async def test_to_game_create(self, load_fixture):
        """Test converting IGDB data to GameCreate schema"""
        fixture_data = load_fixture("igdb", "game_details.json")
        service = IGDBService()

        game_create = service.to_game_create(fixture_data)

        assert "Witcher" in game_create.title
        assert game_create.external_id == "1942"
        assert game_create.external_source == "igdb"
        assert game_create.description is not None
        assert len(game_create.description) > 0

        await service.close()

    @pytest.mark.asyncio
    async def test_platforms_mapping(self, load_fixture):
        """Test platform mapping from IGDB to our enum"""
        fixture_data = load_fixture("igdb", "game_details.json")
        service = IGDBService()

        game_create = service.to_game_create(fixture_data)

        if "platforms" in fixture_data and fixture_data["platforms"]:
            assert game_create.platforms is not None
            assert len(game_create.platforms) > 0

        await service.close()

    @pytest.mark.asyncio
    async def test_get_cover_url(self):
        """Test cover URL building"""
        cover_data = {"url": "//images.igdb.com/igdb/image/upload/t_thumb/test.jpg"}
        url = IGDBService._get_cover_url(cover_data)

        assert url is not None
        assert url.startswith("https://")
        assert "t_cover_big" in url
        assert "test.jpg" in url

        url = IGDBService._get_cover_url(None)
        assert url is None

        url = IGDBService._get_cover_url({})
        assert url is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no results"""
        with patch.object(
            IGDBService, "_check_auth", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = True

            with patch.object(
                IGDBService, "_post", new_callable=AsyncMock
            ) as mock_post:
                mock_post.return_value = []

                async with IGDBService() as service:
                    results = await service.search("xyzinvalid", limit=5)
                    assert results == []

    @pytest.mark.asyncio
    async def test_check_auth_failure(self):
        """Test authentication failure"""
        with patch.object(
            IGDBService, "_check_auth", new_callable=AsyncMock
        ) as mock_auth:
            mock_auth.return_value = False

            service = IGDBService()
            result = await service._query("games", 'search "test";')
            assert result is None

            await service.close()
