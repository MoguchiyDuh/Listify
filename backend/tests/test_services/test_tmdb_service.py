from unittest.mock import AsyncMock, patch

import pytest

from services.tmdb import TMDBService


@pytest.mark.services
class TestTMDBService:
    """Test TMDB service with mocked responses"""

    @pytest.mark.asyncio
    async def test_search_movie(self, load_fixture):
        """Test movie search with mocked response"""
        fixture_data = load_fixture("tmdb", "movie_search.json")

        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"results": fixture_data}

            async with TMDBService() as service:
                results = await service.search("Inception", limit=3, media_type="movie")

                assert results == fixture_data
                assert len(results) == 3
                assert results[0]["id"] == 27205
                assert results[0]["title"] == "Inception"

    @pytest.mark.asyncio
    async def test_search_tv(self, load_fixture):
        """Test TV search with mocked response"""
        fixture_data = load_fixture("tmdb", "tv_search.json")

        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"results": fixture_data}

            async with TMDBService() as service:
                results = await service.search("Breaking Bad", limit=3, media_type="tv")

                assert results == fixture_data
                assert len(results) == 3
                assert results[0]["id"] == 1396
                assert results[0]["name"] == "Breaking Bad"

    @pytest.mark.asyncio
    async def test_get_movie_by_id(self, load_fixture):
        """Test getting movie by ID with mocked response"""
        fixture_data = load_fixture("tmdb", "movie_details.json")

        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = fixture_data

            async with TMDBService() as service:
                movie = await service.get_by_id("27205", media_type="movie")

                assert movie == fixture_data
                assert movie["id"] == 27205
                assert movie["title"] == "Inception"
                assert movie["runtime"] == 148
                assert len(movie["genres"]) == 3

    @pytest.mark.asyncio
    async def test_get_tv_by_id(self, load_fixture):
        """Test getting TV show by ID with mocked response"""
        fixture_data = load_fixture("tmdb", "tv_details.json")

        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = fixture_data

            async with TMDBService() as service:
                tv = await service.get_by_id("1396", media_type="tv")

                assert tv == fixture_data
                assert tv["id"] == 1396
                assert tv["name"] == "Breaking Bad"
                assert tv["number_of_episodes"] == 62
                assert tv["number_of_seasons"] == 5

    @pytest.mark.asyncio
    async def test_get_by_invalid_id(self):
        """Test getting movie with invalid ID"""
        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            async with TMDBService() as service:
                movie = await service.get_by_id("99999999", media_type="movie")
                assert movie is None

    @pytest.mark.asyncio
    async def test_to_movie_create(self, load_fixture):
        """Test converting TMDB movie data to MovieCreate schema"""
        fixture_data = load_fixture("tmdb", "movie_details.json")
        service = TMDBService()

        movie_create = service.to_movie_create(fixture_data)

        assert movie_create.title == "Inception"
        assert movie_create.external_id == "27205"
        assert movie_create.external_source == "tmdb"
        assert movie_create.runtime == 148
        assert movie_create.description is not None
        assert len(movie_create.description) > 0
        assert movie_create.cover_image_url.startswith(
            "https://image.tmdb.org/t/p/original/"
        )
        assert movie_create.release_date is not None
        assert len(movie_create.tags) == 3
        assert "Action" in movie_create.tags

        await service.close()

    @pytest.mark.asyncio
    async def test_to_series_create(self, load_fixture):
        """Test converting TMDB TV data to SeriesCreate schema"""
        fixture_data = load_fixture("tmdb", "tv_details.json")
        service = TMDBService()

        series_create = service.to_series_create(fixture_data)

        assert series_create.title == "Breaking Bad"
        assert series_create.external_id == "1396"
        assert series_create.external_source == "tmdb"
        assert series_create.total_episodes == 62
        assert series_create.seasons == 5
        assert series_create.cover_image_url.startswith(
            "https://image.tmdb.org/t/p/original/"
        )
        assert len(series_create.tags) == 2
        assert "Crime" in series_create.tags

        await service.close()

    @pytest.mark.asyncio
    async def test_get_image_url(self):
        """Test image URL building"""
        url = TMDBService.get_image_url("/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg")
        assert (
            url == "https://image.tmdb.org/t/p/original/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg"
        )

        url = TMDBService.get_image_url(None)
        assert url is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no results"""
        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"results": []}

            async with TMDBService() as service:
                results = await service.search(
                    "xyzinvalid", limit=5, media_type="movie"
                )
                assert results == []

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test handling of HTTP errors"""
        with patch.object(TMDBService, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("HTTP Error")

            async with TMDBService() as service:
                results = await service.search("Inception", media_type="movie")
                assert results == []

    @pytest.mark.asyncio
    async def test_cache_integration(self, load_fixture):
        """Test that service uses cache when available"""
        fixture_data = load_fixture("tmdb", "movie_search.json")
        
        with patch("services.tmdb.cache.get", new_callable=AsyncMock) as mock_cache_get:
            mock_cache_get.return_value = fixture_data
            
            async with TMDBService() as service:
                results = await service.search("Inception", media_type="movie")
                assert results == fixture_data
                mock_cache_get.assert_called_once()
