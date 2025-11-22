from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.routes
class TestSearchRoutes:
    """Test search routes"""

    async def get_auth_token(self, client: AsyncClient, test_user) -> str:
        """Helper to get auth token"""
        response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )
        return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_search_movies(self, client: AsyncClient, test_user, load_fixture):
        """Test searching movies via TMDB"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("tmdb", "movie_search.json")

        with patch("services.tmdb.TMDBService.search", new_callable=AsyncMock) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/movies?q=Inception&limit=3",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "tmdb"
            assert len(data["results"]) == 3

    @pytest.mark.asyncio
    async def test_search_series(self, client: AsyncClient, test_user, load_fixture):
        """Test searching series via TMDB"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("tmdb", "tv_search.json")

        with patch("services.tmdb.TMDBService.search", new_callable=AsyncMock) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/series?q=Breaking+Bad",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "tmdb"
            assert len(data["results"]) > 0

    @pytest.mark.asyncio
    async def test_search_anime(self, client: AsyncClient, test_user, load_fixture):
        """Test searching anime via Jikan"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("jikan", "anime_search.json")

        with patch("services.jikan.JikanService.search", new_callable=AsyncMock) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/anime?q=Steins+Gate",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "jikan"
            assert len(data["results"]) > 0

    @pytest.mark.asyncio
    async def test_search_manga(self, client: AsyncClient, test_user, load_fixture):
        """Test searching manga via Jikan"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("jikan", "manga_search.json")

        with patch("services.jikan.JikanService.search", new_callable=AsyncMock) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/manga?q=Berserk",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "jikan"

    @pytest.mark.asyncio
    async def test_search_books(self, client: AsyncClient, test_user, load_fixture):
        """Test searching books via Open Library"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("openlibrary", "book_search.json")

        with patch(
            "services.openlibrary.OpenLibraryService.search", new_callable=AsyncMock
        ) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/books?q=Dune",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "openlibrary"

    @pytest.mark.asyncio
    async def test_search_games(self, client: AsyncClient, test_user, load_fixture):
        """Test searching games via IGDB"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("igdb", "game_search.json")

        with patch("services.igdb.IGDBService.search", new_callable=AsyncMock) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/games?q=Witcher",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "igdb"

    @pytest.mark.asyncio
    async def test_get_movie_details(self, client: AsyncClient, test_user, load_fixture):
        """Test getting movie details"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("tmdb", "movie_details.json")

        with patch(
            "services.tmdb.TMDBService.get_by_id", new_callable=AsyncMock
        ) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/movies/27205",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "tmdb"
            assert data["result"]["title"] == "Inception"

    @pytest.mark.asyncio
    async def test_get_anime_details(self, client: AsyncClient, test_user, load_fixture):
        """Test getting anime details"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("jikan", "anime_details.json")

        with patch(
            "services.jikan.JikanService.get_by_id", new_callable=AsyncMock
        ) as mock:
            mock.return_value = fixture_data

            response = await client.get(
                "/api/search/anime/9253",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "jikan"

    @pytest.mark.asyncio
    async def test_convert_movie(self, client: AsyncClient, test_user, load_fixture):
        """Test converting TMDB movie data"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("tmdb", "movie_details.json")

        response = await client.post(
            "/api/search/convert/movie",
            json=fixture_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Inception"
        assert data["external_source"] == "tmdb"
        assert isinstance(data["directors"], list)

    @pytest.mark.asyncio
    async def test_convert_anime(self, client: AsyncClient, test_user, load_fixture):
        """Test converting Jikan anime data"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("jikan", "anime_details.json")

        response = await client.post(
            "/api/search/convert/anime",
            json=fixture_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Steins;Gate"
        assert data["external_source"] == "jikan"
        assert isinstance(data["studios"], list)

    @pytest.mark.asyncio
    async def test_convert_manga(self, client: AsyncClient, test_user, load_fixture):
        """Test converting Jikan manga data"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("jikan", "manga_details.json")

        response = await client.post(
            "/api/search/convert/manga",
            json=fixture_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Berserk"
        assert isinstance(data["authors"], list)

    @pytest.mark.asyncio
    async def test_convert_game(self, client: AsyncClient, test_user, load_fixture):
        """Test converting IGDB game data"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("igdb", "game_details.json")

        response = await client.post(
            "/api/search/convert/game",
            json=fixture_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "Witcher" in data["title"]
        assert isinstance(data["developers"], list) or data["developers"] is None
        assert isinstance(data["publishers"], list) or data["publishers"] is None

    @pytest.mark.asyncio
    async def test_convert_book(self, client: AsyncClient, test_user, load_fixture):
        """Test converting Open Library book data"""
        token = await self.get_auth_token(client, test_user)
        fixture_data = load_fixture("openlibrary", "book_search.json")

        response = await client.post(
            "/api/search/convert/book",
            json=fixture_data[0],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] is not None
        assert isinstance(data["authors"], list) or data["authors"] is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_details(self, client: AsyncClient, test_user):
        """Test getting nonexistent media details"""
        token = await self.get_auth_token(client, test_user)

        with patch(
            "services.tmdb.TMDBService.get_by_id", new_callable=AsyncMock
        ) as mock:
            mock.return_value = None

            response = await client.get(
                "/api/search/movies/99999999",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing search without authentication"""
        response = await client.get("/api/search/movies?q=test")

        assert response.status_code == 401
