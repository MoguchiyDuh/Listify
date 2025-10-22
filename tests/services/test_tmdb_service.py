from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from app.schemas.movie import MovieCreate
from app.schemas.series import SeriesCreate
from app.services.tmdb import TMDBService


@pytest.mark.services
class TestTMDBService:
    """Test TMDB service."""

    @pytest_asyncio.fixture
    async def tmdb_service(self):
        """Create TMDB service instance."""
        service = TMDBService()
        yield service
        await service.close()

    @pytest.fixture
    def mock_movie_data(self):
        """Mock TMDB movie data."""
        return {
            "id": 550,
            "title": "Fight Club",
            "overview": "A ticking-time-bomb insomniac and a slippery soap salesman...",
            "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
            "release_date": "1999-10-15",
            "runtime": 139,
            "credits": {
                "crew": [
                    {"name": "David Fincher", "job": "Director"},
                    {"name": "Someone Else", "job": "Producer"},
                ]
            },
        }

    @pytest.fixture
    def mock_tv_data(self):
        """Mock TMDB TV data."""
        return {
            "id": 1396,
            "name": "Breaking Bad",
            "overview": "A high school chemistry teacher...",
            "poster_path": "/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
            "first_air_date": "2008-01-20",
            "number_of_episodes": 62,
            "number_of_seasons": 5,
            "status": "Ended",
        }

    @pytest.mark.asyncio
    async def test_search_movies(self, tmdb_service, mock_movie_data):
        """Test searching for movies."""
        mock_response = {"results": [mock_movie_data]}

        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            results = await tmdb_service.search_movies("Fight Club", limit=10)

            assert len(results) == 1
            assert results[0]["title"] == "Fight Club"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_tv(self, tmdb_service, mock_tv_data):
        """Test searching for TV shows."""
        mock_response = {"results": [mock_tv_data]}

        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            results = await tmdb_service.search_tv("Breaking Bad", limit=10)

            assert len(results) == 1
            assert results[0]["name"] == "Breaking Bad"
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_multi(self, tmdb_service):
        """Test multi-search."""
        mock_response = {
            "results": [
                {"media_type": "movie", "title": "Test Movie"},
                {"media_type": "tv", "name": "Test Show"},
                {"media_type": "person", "name": "Test Person"},
            ]
        }

        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            results = await tmdb_service.search("test", limit=10)

            assert len(results) == 2  # Person filtered out
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_movie_details(self, tmdb_service, mock_movie_data):
        """Test getting movie details."""
        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_movie_data

            result = await tmdb_service.get_movie_details("550")

            assert result["title"] == "Fight Club"
            assert result["runtime"] == 139
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tv_details(self, tmdb_service, mock_tv_data):
        """Test getting TV details."""
        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tv_data

            result = await tmdb_service.get_tv_details("1396")

            assert result["name"] == "Breaking Bad"
            assert result["number_of_seasons"] == 5
            mock_get.assert_called_once()

    def test_to_movie_create(self, tmdb_service, mock_movie_data):
        """Test converting TMDB data to MovieCreate schema."""
        movie = tmdb_service.to_movie_create(mock_movie_data)

        assert isinstance(movie, MovieCreate)
        assert movie.title == "Fight Club"
        assert movie.runtime == 139
        assert movie.director == "David Fincher"
        assert movie.release_date == date(1999, 10, 15)
        assert movie.is_custom is False
        assert "w500" in movie.image

    def test_to_movie_create_no_credits(self, tmdb_service):
        """Test converting TMDB data without credits."""
        data = {
            "title": "Test Movie",
            "overview": "Test overview",
            "release_date": "2024-01-01",
            "poster_path": "/test.jpg",
            "runtime": 120,
        }

        movie = tmdb_service.to_movie_create(data)

        assert movie.title == "Test Movie"
        assert movie.director is None

    def test_to_series_create(self, tmdb_service, mock_tv_data):
        """Test converting TMDB data to SeriesCreate schema."""
        series = tmdb_service.to_series_create(mock_tv_data)

        assert isinstance(series, SeriesCreate)
        assert series.title == "Breaking Bad"
        assert series.total_episodes == 62
        assert series.seasons == 5
        assert series.release_date == date(2008, 1, 20)
        assert series.is_custom is False

    def test_to_series_create_airing(self, tmdb_service):
        """Test converting airing series."""
        data = {
            "name": "Test Series",
            "overview": "Test overview",
            "first_air_date": "2024-01-01",
            "poster_path": "/test.jpg",
            "number_of_episodes": 10,
            "number_of_seasons": 1,
            "status": "Returning Series",
        }

        series = tmdb_service.to_series_create(data)

        from app.models.media import AnimeSeriesStatusEnum

        assert series.status == AnimeSeriesStatusEnum.AIRING

    def test_get_image_url(self):
        """Test building image URL."""
        url = TMDBService.get_image_url("/test.jpg")
        assert url == "https://image.tmdb.org/t/p/w500/test.jpg"

        url = TMDBService.get_image_url(None)
        assert url is None

    @pytest.mark.asyncio
    async def test_search_empty_results(self, tmdb_service):
        """Test search with no results."""
        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"results": []}

            results = await tmdb_service.search_movies("nonexistent")

            assert results == []

    @pytest.mark.asyncio
    async def test_search_api_error(self, tmdb_service):
        """Test search with API error."""
        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            results = await tmdb_service.search_movies("test")

            assert results == []

    @pytest.mark.asyncio
    async def test_get_details_not_found(self, tmdb_service):
        """Test getting details for non-existent movie."""
        with patch.object(tmdb_service, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await tmdb_service.get_movie_details("999999")

            assert result is None
