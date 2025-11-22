from datetime import date

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import PermissionDenied
from crud import media_crud, user_crud
from models import MediaTypeEnum
from schemas import (AnimeCreate, BookCreate, GameCreate, MangaCreate,
                     MovieCreate, SeriesCreate)


@pytest.mark.crud
class TestMediaCRUD:
    """Test Media CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_movie(self, clean_db: AsyncSession):
        """Test creating a movie"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test movie",
            release_date=date(2024, 1, 1),
            external_id="12345",
            external_source="tmdb",
            runtime=120,
            directors=["Christopher Nolan", "Denis Villeneuve"],
        )

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        assert movie.id is not None
        assert movie.title == "Test Movie"
        assert movie.description == "A test movie"
        assert movie.media_type == MediaTypeEnum.MOVIE
        assert movie.external_id == "12345"
        assert movie.external_source == "tmdb"
        assert movie.is_custom is False
        assert movie.runtime == 120
        assert movie.directors == ["Christopher Nolan", "Denis Villeneuve"]

    @pytest.mark.asyncio
    async def test_create_series(self, clean_db: AsyncSession):
        """Test creating a series"""
        series_data = SeriesCreate(
            title="Test Series",
            description="A test series",
            release_date=date(2024, 1, 1),
            external_id="67890",
            external_source="tmdb",
            seasons=3,
            total_episodes=30,
        )

        series = await media_crud.create_series(db=clean_db, obj_in=series_data)

        assert series.id is not None
        assert series.title == "Test Series"
        assert series.media_type == MediaTypeEnum.SERIES
        assert series.seasons == 3
        assert series.total_episodes == 30

    @pytest.mark.asyncio
    async def test_create_anime(self, clean_db: AsyncSession):
        """Test creating an anime"""
        anime_data = AnimeCreate(
            title="Test Anime",
            description="A test anime",
            release_date=date(2024, 1, 1),
            external_id="1",
            external_source="jikan",
            total_episodes=12,
            studios=["Kyoto Animation", "Ufotable"],
        )

        anime = await media_crud.create_anime(db=clean_db, obj_in=anime_data)

        assert anime.id is not None
        assert anime.title == "Test Anime"
        assert anime.media_type == MediaTypeEnum.ANIME
        assert anime.total_episodes == 12
        assert anime.studios == ["Kyoto Animation", "Ufotable"]

    @pytest.mark.asyncio
    async def test_create_manga(self, clean_db: AsyncSession):
        """Test creating a manga"""
        manga_data = MangaCreate(
            title="Test Manga",
            description="A test manga",
            release_date=date(2024, 1, 1),
            external_id="2",
            external_source="jikan",
            total_chapters=50,
            total_volumes=5,
            authors=["Kentaro Miura", "Hajime Isayama"],
        )

        manga = await media_crud.create_manga(db=clean_db, obj_in=manga_data)

        assert manga.id is not None
        assert manga.title == "Test Manga"
        assert manga.media_type == MediaTypeEnum.MANGA
        assert manga.total_chapters == 50
        assert manga.total_volumes == 5
        assert manga.authors == ["Kentaro Miura", "Hajime Isayama"]

    @pytest.mark.asyncio
    async def test_create_book(self, clean_db: AsyncSession):
        """Test creating a book"""
        book_data = BookCreate(
            title="Test Book",
            description="A test book",
            release_date=date(2024, 1, 1),
            external_id="abc123",
            external_source="openlibrary",
            authors=["Test Author"],
            pages=300,
        )

        book = await media_crud.create_book(db=clean_db, obj_in=book_data)

        assert book.id is not None
        assert book.title == "Test Book"
        assert book.media_type == MediaTypeEnum.BOOK
        assert book.authors == ["Test Author"]
        assert book.pages == 300

    @pytest.mark.asyncio
    async def test_create_game(self, clean_db: AsyncSession):
        """Test creating a game"""
        game_data = GameCreate(
            title="Test Game",
            description="A test game",
            release_date=date(2024, 1, 1),
            external_id="999",
            external_source="igdb",
            developers=["Test Dev"],
            publishers=["Test Pub"],
        )

        game = await media_crud.create_game(db=clean_db, obj_in=game_data)

        assert game.id is not None
        assert game.title == "Test Game"
        assert game.media_type == MediaTypeEnum.GAME
        assert game.developers == ["Test Dev"]
        assert game.publishers == ["Test Pub"]

    @pytest.mark.asyncio
    async def test_create_custom_media_with_user(
        self, test_user, clean_db: AsyncSession
    ):
        """Test creating custom media with user ownership"""

        movie_data = MovieCreate(
            title="Custom Movie",
            description="User custom movie",
            is_custom=True,
        )

        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=test_user.id
        )

        assert movie.is_custom is True
        assert movie.created_by_id == test_user.id

    @pytest.mark.asyncio
    async def test_create_media_with_tags(self, clean_db: AsyncSession):
        """Test creating media with tags"""
        movie_data = MovieCreate(
            title="Tagged Movie",
            description="Movie with tags",
            tags=["action", "sci-fi", "thriller"],
        )

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        assert movie.id is not None

        # Get tags separately to avoid lazy loading issue
        from crud.tag import tag_crud

        tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        assert len(tags) == 3
        tag_names = [tag.name for tag in tags]
        assert "action" in tag_names
        assert "sci-fi" in tag_names
        assert "thriller" in tag_names

    @pytest.mark.asyncio
    async def test_create_duplicate_external_media(self, clean_db: AsyncSession):
        """Test creating duplicate external media returns existing"""
        movie_data = MovieCreate(
            title="Duplicate Movie",
            description="First instance",
            external_id="duplicate123",
            external_source="tmdb",
        )

        movie1 = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        duplicate_data = MovieCreate(
            title="Different Title",
            description="Second instance",
            external_id="duplicate123",
            external_source="tmdb",
        )

        movie2 = await media_crud.create_movie(db=clean_db, obj_in=duplicate_data)

        assert movie1.id == movie2.id
        assert movie1.title == movie2.title

    @pytest.mark.asyncio
    async def test_get_media_by_id(self, clean_db: AsyncSession):
        """Test getting media by ID"""
        movie_data = MovieCreate(title="Test Movie", description="A test")

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)
        fetched = await media_crud.get_by_id(db=clean_db, id=movie.id)

        assert fetched is not None
        assert fetched.id == movie.id
        assert fetched.title == movie.title

    @pytest.mark.asyncio
    async def test_get_media_by_id_with_type_filter(self, clean_db: AsyncSession):
        """Test getting media by ID with type filter"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        fetched = await media_crud.get_by_id(
            db=clean_db, id=movie.id, media_type=MediaTypeEnum.MOVIE
        )
        assert fetched is not None

        fetched_wrong_type = await media_crud.get_by_id(
            db=clean_db, id=movie.id, media_type=MediaTypeEnum.SERIES
        )
        assert fetched_wrong_type is None

    @pytest.mark.asyncio
    async def test_get_all_media(self, clean_db: AsyncSession):
        """Test getting all media"""
        await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 1", description="Test")
        )
        await media_crud.create_series(
            db=clean_db, obj_in=SeriesCreate(title="Series 1", description="Test")
        )
        await media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime 1", description="Test")
        )

        all_media = await media_crud.get_all(db=clean_db)

        assert len(all_media) == 3

    @pytest.mark.asyncio
    async def test_get_all_media_filtered_by_type(self, clean_db: AsyncSession):
        """Test getting all media filtered by type"""
        await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 1", description="Test")
        )
        await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 2", description="Test")
        )
        await media_crud.create_series(
            db=clean_db, obj_in=SeriesCreate(title="Series 1", description="Test")
        )

        movies = await media_crud.get_all(db=clean_db, media_type=MediaTypeEnum.MOVIE)

        assert len(movies) == 2
        assert all(m.media_type == MediaTypeEnum.MOVIE for m in movies)

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, clean_db: AsyncSession):
        """Test pagination"""
        for i in range(5):
            await media_crud.create_movie(
                db=clean_db, obj_in=MovieCreate(title=f"Movie {i}", description="Test")
            )

        page1 = await media_crud.get_all(db=clean_db, skip=0, limit=2)
        assert len(page1) == 2

        page2 = await media_crud.get_all(db=clean_db, skip=2, limit=2)
        assert len(page2) == 2

        page3 = await media_crud.get_all(db=clean_db, skip=4, limit=2)
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_search_media_by_title(self, clean_db: AsyncSession):
        """Test searching media by title"""
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Wars", description="Sci-fi epic"),
        )
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Trek", description="Space exploration"),
        )
        await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="The Matrix", description="Cyberpunk")
        )

        results = await media_crud.search(db=clean_db, query="Star")

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_media_by_description(self, clean_db: AsyncSession):
        """Test searching media by description"""
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 1", description="A cyberpunk adventure"),
        )
        await media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 2", description="A fantasy journey"),
        )

        results = await media_crud.search(db=clean_db, query="cyberpunk")

        assert len(results) == 1
        assert results[0].title == "Movie 1"

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, clean_db: AsyncSession):
        """Test case-insensitive search"""
        await media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="The Matrix", description="Sci-fi")
        )

        results = await media_crud.search(db=clean_db, query="matrix")
        assert len(results) == 1

        results = await media_crud.search(db=clean_db, query="MATRIX")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_by_external_id(self, clean_db: AsyncSession):
        """Test getting media by external ID"""
        movie_data = MovieCreate(
            title="External Movie",
            external_id="ext123",
            external_source="tmdb",
        )

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        fetched = await media_crud.get_by_external_id(
            db=clean_db,
            external_id="ext123",
            external_source="tmdb",
            media_type=MediaTypeEnum.MOVIE,
        )

        assert fetched is not None
        assert fetched.id == movie.id

    @pytest.mark.asyncio
    async def test_update_movie(self, test_user, clean_db: AsyncSession):
        """Test updating a movie"""
        movie_data = MovieCreate(
            title="Original Title",
            description="Original description",
            is_custom=True,
        )

        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=test_user.id
        )

        update_data = MovieCreate(
            title="Updated Title",
            description="Updated description",
        )

        updated = await media_crud.update_movie(
            db=clean_db, id=movie.id, obj_in=update_data, user_id=test_user.id
        )

        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_non_custom_media_fails(
        self, test_user, clean_db: AsyncSession
    ):
        """Test updating non-custom media raises error"""
        movie_data = MovieCreate(
            title="External Movie",
            external_id="123",
            external_source="tmdb",
            is_custom=False,
        )

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        update_data = MovieCreate(title="Updated Title")

        with pytest.raises(PermissionDenied):
            await media_crud.update_movie(
                db=clean_db, id=movie.id, obj_in=update_data, user_id=test_user.id
            )

    @pytest.mark.asyncio
    async def test_update_other_user_media_fails(self, clean_db: AsyncSession):
        """Test updating another user's media raises error"""
        user1 = await user_crud.create(
            db=clean_db,
            username="user1",
            email="user1@example.com",
            password="password123",
        )
        user2 = await user_crud.create(
            db=clean_db,
            username="user2",
            email="user2@example.com",
            password="password123",
        )

        movie_data = MovieCreate(title="User1 Movie", is_custom=True)
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=user1.id
        )

        update_data = MovieCreate(title="Updated by User2")

        with pytest.raises(PermissionDenied):
            await media_crud.update_movie(
                db=clean_db, id=movie.id, obj_in=update_data, user_id=user2.id
            )

    @pytest.mark.asyncio
    async def test_update_media_tags(self, test_user, clean_db: AsyncSession):
        """Test updating media with tags"""
        movie_data = MovieCreate(
            title="Tagged Movie",
            tags=["action", "sci-fi"],
            is_custom=True,
        )

        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=test_user.id
        )

        # Check initial tags
        from crud.tag import tag_crud

        initial_tags = await tag_crud.get_tags_for_media(db=clean_db, media_id=movie.id)
        assert len(initial_tags) == 2

        update_data = MovieCreate(
            title="Tagged Movie",
            description="Test",
            tags=["action", "thriller", "drama"],
        )

        updated = await media_crud.update_movie(
            db=clean_db, id=movie.id, obj_in=update_data, user_id=test_user.id
        )

        # Check updated tags
        updated_tags = await tag_crud.get_tags_for_media(
            db=clean_db, media_id=updated.id
        )
        assert len(updated_tags) == 3
        tag_names = [tag.name for tag in updated_tags]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "drama" in tag_names
        assert "sci-fi" not in tag_names

    @pytest.mark.asyncio
    async def test_delete_media(self, test_user, clean_db: AsyncSession):
        """Test deleting media"""

        movie_data = MovieCreate(title="Delete Me", is_custom=True)
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=test_user.id
        )

        result = await media_crud.delete(db=clean_db, id=movie.id, user_id=test_user.id)

        assert result is True

        fetched = await media_crud.get_by_id(db=clean_db, id=movie.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_non_custom_media_fails(
        self, test_user, clean_db: AsyncSession
    ):
        """Test deleting non-custom media raises error"""

        movie_data = MovieCreate(
            title="External Movie",
            external_id="123",
            external_source="tmdb",
            is_custom=False,
        )

        movie = await media_crud.create_movie(db=clean_db, obj_in=movie_data)

        with pytest.raises(PermissionDenied):
            await media_crud.delete(db=clean_db, id=movie.id, user_id=test_user.id)

    @pytest.mark.asyncio
    async def test_delete_other_user_media_fails(self, clean_db: AsyncSession):
        """Test deleting another user's media raises error"""
        user1 = await user_crud.create(
            db=clean_db,
            username="user1",
            email="user1@example.com",
            password="password123",
        )
        user2 = await user_crud.create(
            db=clean_db,
            username="user2",
            email="user2@example.com",
            password="password123",
        )

        movie_data = MovieCreate(title="User1 Movie", is_custom=True)
        movie = await media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=user1.id
        )

        with pytest.raises(PermissionDenied):
            await media_crud.delete(db=clean_db, id=movie.id, user_id=user2.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_media(self, clean_db: AsyncSession):
        """Test deleting non-existent media"""
        result = await media_crud.delete(db=clean_db, id=999)
        assert result is False
