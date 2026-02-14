from unittest.mock import AsyncMock, patch

import pytest

from services.jikan import JikanService


@pytest.mark.services
class TestJikanService:
    """Test Jikan service with mocked responses"""

    @pytest.mark.asyncio
    async def test_search_anime(self, load_fixture):
        """Test anime search with mocked response"""
        fixture_data = load_fixture("jikan", "anime_search.json")

        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": fixture_data}

            async with JikanService() as service:
                results = await service.search(
                    "Steins Gate", limit=3, media_type="anime"
                )

                assert results == fixture_data
                assert len(results) == 3
                assert results[0]["mal_id"] == 9253
                assert results[0]["title"] == "Steins;Gate"

                mock_get.assert_called_once_with(
                    "anime", {"q": "Steins Gate", "limit": 3, "sfw": "false"}, cache_ttl=3600
                )

    @pytest.mark.asyncio
    async def test_search_manga(self, load_fixture):
        """Test manga search with mocked response"""
        fixture_data = load_fixture("jikan", "manga_search.json")

        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": fixture_data}

            async with JikanService() as service:
                results = await service.search("Berserk", limit=3, media_type="manga")

                assert results == fixture_data
                assert len(results) == 3
                assert results[0]["mal_id"] == 2
                assert results[0]["title"] == "Berserk"

    @pytest.mark.asyncio
    async def test_get_anime_by_id(self, load_fixture):
        """Test getting anime by ID with mocked response"""
        fixture_data = load_fixture("jikan", "anime_details.json")

        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": fixture_data}

            async with JikanService() as service:
                anime = await service.get_by_id("9253", media_type="anime")

                assert anime == fixture_data
                assert anime["mal_id"] == 9253
                assert anime["title"] == "Steins;Gate"
                assert anime["episodes"] == 24
                assert len(anime["studios"]) == 1
                assert anime["studios"][0]["name"] == "White Fox"

    @pytest.mark.asyncio
    async def test_get_manga_by_id(self, load_fixture):
        """Test getting manga by ID with mocked response"""
        fixture_data = load_fixture("jikan", "manga_details.json")

        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": fixture_data}

            async with JikanService() as service:
                manga = await service.get_by_id("2", media_type="manga")

                assert manga == fixture_data
                assert manga["mal_id"] == 2
                assert manga["title"] == "Berserk"
                assert len(manga["authors"]) == 2

    @pytest.mark.asyncio
    async def test_get_by_invalid_id(self):
        """Test getting anime with invalid ID"""
        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            async with JikanService() as service:
                anime = await service.get_by_id("99999999", media_type="anime")
                assert anime is None

    @pytest.mark.asyncio
    async def test_to_anime_create(self, load_fixture):
        """Test converting Jikan anime data to AnimeCreate schema"""
        fixture_data = load_fixture("jikan", "anime_details.json")
        service = JikanService()

        anime_create = service.to_anime_create(fixture_data)

        assert anime_create.title == "Steins;Gate"
        assert anime_create.external_id == "9253"
        assert anime_create.external_source == "jikan"
        assert anime_create.total_episodes == 24
        assert anime_create.studios == ["White Fox"]
        assert (
            anime_create.cover_image_url
            == "https://cdn.myanimelist.net/images/anime/1935/127974l.jpg"
        )
        assert len(anime_create.tags) >= 5
        assert "Drama" in anime_create.tags
        assert "Sci-Fi" in anime_create.tags
        assert "Psychological" in anime_create.tags

        await service.close()

    @pytest.mark.asyncio
    async def test_to_manga_create(self, load_fixture):
        """Test converting Jikan manga data to MangaCreate schema"""
        fixture_data = load_fixture("jikan", "manga_details.json")
        service = JikanService()

        manga_create = service.to_manga_create(fixture_data)

        assert manga_create.title == "Berserk"
        assert manga_create.external_id == "2"
        assert manga_create.external_source == "jikan"
        assert manga_create.authors == ["Miura, Kentarou", "Studio Gaga"]
        assert (
            manga_create.cover_image_url
            == "https://cdn.myanimelist.net/images/manga/1/157897l.jpg"
        )
        assert len(manga_create.tags) >= 9
        assert "Action" in manga_create.tags
        assert "Gore" in manga_create.tags

        await service.close()

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no results"""
        with patch.object(JikanService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"data": []}

            async with JikanService() as service:
                results = await service.search(
                    "xyzinvalid", limit=5, media_type="anime"
                )
                assert results == []
