from datetime import date

import pytest
from httpx import AsyncClient

from crud import media_crud
from models import MediaTypeEnum
from schemas import AnimeCreate, BookCreate, GameCreate, MangaCreate, MovieCreate


@pytest.mark.routes
class TestMediaRoutes:
    """Test media routes"""

    async def get_auth_token(self, client: AsyncClient, test_user) -> str:
        """Helper to get auth token"""
        response = await client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": "testpass123"},
        )
        return response.json()["access_token"]

    # Movie endpoints
    @pytest.mark.asyncio
    async def test_create_movie(self, client: AsyncClient, test_user):
        """Test creating a movie"""
        token = await self.get_auth_token(client, test_user)

        response = await client.post(
            "/api/media/movies",
            json={
                "title": "Test Movie",
                "description": "A test movie",
                "directors": ["Christopher Nolan"],
                "runtime": 148,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Movie"
        assert data["media_type"] == "movie"
        assert data["directors"] == ["Christopher Nolan"]

    @pytest.mark.asyncio
    async def test_get_movies(self, client: AsyncClient, test_user, clean_db):
        """Test getting all movies"""
        token = await self.get_auth_token(client, test_user)

        # Create test movie
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(
                title="Movie 1",
                description="Test",
                directors=["Director 1"],
            ),
        )

        response = await client.get(
            "/api/media/movies",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Movie 1"

    @pytest.mark.asyncio
    async def test_get_movie_by_id(self, client: AsyncClient, test_user, clean_db):
        """Test getting specific movie"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Test Movie", description="Test"),
        )

        response = await client.get(
            f"/api/media/movies/{movie.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == movie.id
        assert data["title"] == "Test Movie"

    @pytest.mark.asyncio
    async def test_get_nonexistent_movie(self, client: AsyncClient, test_user):
        """Test getting nonexistent movie"""
        token = await self.get_auth_token(client, test_user)

        response = await client.get(
            "/api/media/movies/99999",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_movie(self, client: AsyncClient, test_user, clean_db):
        """Test updating a movie"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(
                title="Original",
                description="Test",
                is_custom=True,
            ),
            user_id=test_user.id,
        )

        response = await client.put(
            f"/api/media/movies/{movie.id}",
            json={"title": "Updated", "description": "Updated description"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"

    @pytest.mark.asyncio
    async def test_delete_movie(self, client: AsyncClient, test_user, clean_db):
        """Test deleting a movie"""
        token = await self.get_auth_token(client, test_user)

        movie = await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="To Delete", is_custom=True),
            user_id=test_user.id,
        )

        response = await client.delete(
            f"/api/media/movies/{movie.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

    # Anime endpoints
    @pytest.mark.asyncio
    async def test_create_anime(self, client: AsyncClient, test_user):
        """Test creating anime"""
        token = await self.get_auth_token(client, test_user)

        response = await client.post(
            "/api/media/anime",
            json={
                "title": "Test Anime",
                "description": "A test anime",
                "studios": ["Kyoto Animation"],
                "total_episodes": 24,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Anime"
        assert data["studios"] == ["Kyoto Animation"]

    # Manga endpoints
    @pytest.mark.asyncio
    async def test_create_manga(self, client: AsyncClient, test_user):
        """Test creating manga"""
        token = await self.get_auth_token(client, test_user)

        response = await client.post(
            "/api/media/manga",
            json={
                "title": "Test Manga",
                "description": "A test manga",
                "authors": ["Kentaro Miura"],
                "total_chapters": 364,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Manga"
        assert data["authors"] == ["Kentaro Miura"]

    # Book endpoints
    @pytest.mark.asyncio
    async def test_create_book(self, client: AsyncClient, test_user):
        """Test creating a book"""
        token = await self.get_auth_token(client, test_user)

        response = await client.post(
            "/api/media/books",
            json={
                "title": "Test Book",
                "description": "A test book",
                "authors": ["Frank Herbert"],
                "pages": 600,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["authors"] == ["Frank Herbert"]

    # Game endpoints
    @pytest.mark.asyncio
    async def test_create_game(self, client: AsyncClient, test_user):
        """Test creating a game"""
        token = await self.get_auth_token(client, test_user)

        response = await client.post(
            "/api/media/games",
            json={
                "title": "Test Game",
                "description": "A test game",
                "developers": ["CD Projekt Red"],
                "publishers": ["CD Projekt"],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Game"
        assert data["developers"] == ["CD Projekt Red"]
        assert data["publishers"] == ["CD Projekt"]

    # Search endpoint in media router
    @pytest.mark.asyncio
    async def test_search_media(self, client: AsyncClient, test_user, clean_db):
        """Test searching media"""
        token = await self.get_auth_token(client, test_user)

        # Create test media
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Wars", description="Epic"),
        )
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Trek", description="Space"),
        )

        response = await client.get(
            "/api/media/search?q=Star",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing media without authentication"""
        response = await client.get("/api/media/movies")

        assert response.status_code == 401
