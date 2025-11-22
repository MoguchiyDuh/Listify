from datetime import date

import pytest
from crud.media import media_crud
from crud.user import user_crud
from models import MediaTypeEnum
from schemas.anime import AnimeCreate
from schemas.book import BookCreate
from schemas.game import GameCreate
from schemas.manga import MangaCreate
from schemas.movie import MovieCreate
from schemas.series import SeriesCreate
from sqlalchemy.orm import Session


@pytest.mark.crud
class TestMediaCRUD:
    """Test Media CRUD operations"""

    def test_create_movie(self, clean_db: Session):
        """Test creating a movie"""
        movie_data = MovieCreate(
            title="Test Movie",
            description="A test movie",
            release_date=date(2024, 1, 1),
            external_id="12345",
            external_source="tmdb",
            runtime=120,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        assert movie.id is not None
        assert movie.title == "Test Movie"
        assert movie.description == "A test movie"
        assert movie.media_type == MediaTypeEnum.MOVIE
        assert movie.external_id == "12345"
        assert movie.external_source == "tmdb"
        assert movie.is_custom is False

    def test_create_series(self, clean_db: Session):
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

        series = media_crud.create_series(db=clean_db, obj_in=series_data)

        assert series.id is not None
        assert series.title == "Test Series"
        assert series.media_type == MediaTypeEnum.SERIES
        assert series.seasons == 3
        assert series.total_episodes == 30

    def test_create_anime(self, clean_db: Session):
        """Test creating an anime"""
        anime_data = AnimeCreate(
            title="Test Anime",
            description="A test anime",
            release_date=date(2024, 1, 1),
            external_id="1",
            external_source="jikan",
            total_episodes=12,
        )

        anime = media_crud.create_anime(db=clean_db, obj_in=anime_data)

        assert anime.id is not None
        assert anime.title == "Test Anime"
        assert anime.media_type == MediaTypeEnum.ANIME
        assert anime.total_episodes == 12

    def test_create_manga(self, clean_db: Session):
        """Test creating a manga"""
        manga_data = MangaCreate(
            title="Test Manga",
            description="A test manga",
            release_date=date(2024, 1, 1),
            external_id="2",
            external_source="jikan",
            total_chapters=50,
            total_volumes=5,
        )

        manga = media_crud.create_manga(db=clean_db, obj_in=manga_data)

        assert manga.id is not None
        assert manga.title == "Test Manga"
        assert manga.media_type == MediaTypeEnum.MANGA
        assert manga.total_chapters == 50
        assert manga.total_volumes == 5

    def test_create_book(self, clean_db: Session):
        """Test creating a book"""
        book_data = BookCreate(
            title="Test Book",
            description="A test book",
            release_date=date(2024, 1, 1),
            external_id="abc123",
            external_source="openlibrary",
            author="Test Author",
            pages=300,
        )

        book = media_crud.create_book(db=clean_db, obj_in=book_data)

        assert book.id is not None
        assert book.title == "Test Book"
        assert book.media_type == MediaTypeEnum.BOOK
        assert book.author == "Test Author"
        assert book.pages == 300

    def test_create_game(self, clean_db: Session):
        """Test creating a game"""
        game_data = GameCreate(
            title="Test Game",
            description="A test game",
            release_date=date(2024, 1, 1),
            external_id="999",
            external_source="igdb",
            developer="Test Dev",
            publisher="Test Pub",
        )

        game = media_crud.create_game(db=clean_db, obj_in=game_data)

        assert game.id is not None
        assert game.title == "Test Game"
        assert game.media_type == MediaTypeEnum.GAME
        assert game.developer == "Test Dev"
        assert game.publisher == "Test Pub"

    def test_create_custom_media_with_user(self, clean_db: Session):
        """Test creating custom media with user ownership"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(
            title="Custom Movie",
            description="User custom movie",
            is_custom=True,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data, user_id=user.id)

        assert movie.is_custom is True
        assert movie.created_by_id == user.id

    def test_create_media_with_tags(self, clean_db: Session):
        """Test creating media with tags"""
        movie_data = MovieCreate(
            title="Tagged Movie",
            description="Movie with tags",
            tags=["action", "sci-fi", "thriller"],
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        assert movie.id is not None
        assert len(movie.tag_associations) == 3
        tag_names = [assoc.tag.name for assoc in movie.tag_associations]
        assert "action" in tag_names
        assert "sci-fi" in tag_names
        assert "thriller" in tag_names

    def test_create_duplicate_external_media(self, clean_db: Session):
        """Test creating duplicate external media returns existing"""
        movie_data = MovieCreate(
            title="Duplicate Movie",
            description="First instance",
            external_id="duplicate123",
            external_source="tmdb",
        )

        movie1 = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        duplicate_data = MovieCreate(
            title="Different Title",
            description="Second instance",
            external_id="duplicate123",
            external_source="tmdb",
        )

        movie2 = media_crud.create_movie(db=clean_db, obj_in=duplicate_data)

        assert movie1.id == movie2.id
        assert movie1.title == movie2.title

    def test_get_media_by_id(self, clean_db: Session):
        """Test getting media by ID"""
        movie_data = MovieCreate(title="Test Movie", description="A test")

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)
        fetched = media_crud.get_by_id(db=clean_db, id=movie.id)

        assert fetched is not None
        assert fetched.id == movie.id
        assert fetched.title == movie.title

    def test_get_media_by_id_with_type_filter(self, clean_db: Session):
        """Test getting media by ID with type filter"""
        movie_data = MovieCreate(title="Test Movie", description="A test")
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        fetched = media_crud.get_by_id(
            db=clean_db, id=movie.id, media_type=MediaTypeEnum.MOVIE
        )
        assert fetched is not None

        fetched_wrong_type = media_crud.get_by_id(
            db=clean_db, id=movie.id, media_type=MediaTypeEnum.SERIES
        )
        assert fetched_wrong_type is None

    def test_get_all_media(self, clean_db: Session):
        """Test getting all media"""
        media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 1", description="Test")
        )
        media_crud.create_series(
            db=clean_db, obj_in=SeriesCreate(title="Series 1", description="Test")
        )
        media_crud.create_anime(
            db=clean_db, obj_in=AnimeCreate(title="Anime 1", description="Test")
        )

        all_media = media_crud.get_all(db=clean_db)

        assert len(all_media) == 3

    def test_get_all_media_filtered_by_type(self, clean_db: Session):
        """Test getting all media filtered by type"""
        media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 1", description="Test")
        )
        media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="Movie 2", description="Test")
        )
        media_crud.create_series(
            db=clean_db, obj_in=SeriesCreate(title="Series 1", description="Test")
        )

        movies = media_crud.get_all(db=clean_db, media_type=MediaTypeEnum.MOVIE)

        assert len(movies) == 2
        assert all(m.media_type == MediaTypeEnum.MOVIE for m in movies)

    def test_get_all_with_pagination(self, clean_db: Session):
        """Test pagination"""
        for i in range(5):
            media_crud.create_movie(
                db=clean_db, obj_in=MovieCreate(title=f"Movie {i}", description="Test")
            )

        page1 = media_crud.get_all(db=clean_db, skip=0, limit=2)
        assert len(page1) == 2

        page2 = media_crud.get_all(db=clean_db, skip=2, limit=2)
        assert len(page2) == 2

        page3 = media_crud.get_all(db=clean_db, skip=4, limit=2)
        assert len(page3) == 1

    def test_search_media_by_title(self, clean_db: Session):
        """Test searching media by title"""
        media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Wars", description="Sci-fi epic"),
        )
        media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Star Trek", description="Space exploration"),
        )
        media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="The Matrix", description="Cyberpunk")
        )

        results = media_crud.search(db=clean_db, query="Star")

        assert len(results) == 2

    def test_search_media_by_description(self, clean_db: Session):
        """Test searching media by description"""
        media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 1", description="A cyberpunk adventure"),
        )
        media_crud.create_movie(
            db=clean_db,
            obj_in=MovieCreate(title="Movie 2", description="A fantasy journey"),
        )

        results = media_crud.search(db=clean_db, query="cyberpunk")

        assert len(results) == 1
        assert results[0].title == "Movie 1"

    def test_search_case_insensitive(self, clean_db: Session):
        """Test case-insensitive search"""
        media_crud.create_movie(
            db=clean_db, obj_in=MovieCreate(title="The Matrix", description="Sci-fi")
        )

        results = media_crud.search(db=clean_db, query="matrix")
        assert len(results) == 1

        results = media_crud.search(db=clean_db, query="MATRIX")
        assert len(results) == 1

    def test_get_by_external_id(self, clean_db: Session):
        """Test getting media by external ID"""
        movie_data = MovieCreate(
            title="External Movie",
            external_id="ext123",
            external_source="tmdb",
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        fetched = media_crud.get_by_external_id(
            db=clean_db,
            external_id="ext123",
            external_source="tmdb",
            media_type=MediaTypeEnum.MOVIE,
        )

        assert fetched is not None
        assert fetched.id == movie.id

    def test_update_movie(self, clean_db: Session):
        """Test updating a movie"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(
            title="Original Title",
            description="Original description",
            is_custom=True,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data, user_id=user.id)

        update_data = MovieCreate(
            title="Updated Title",
            description="Updated description",
        )

        updated = media_crud.update_movie(
            db=clean_db, id=movie.id, obj_in=update_data, user_id=user.id
        )

        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"

    def test_update_non_custom_media_fails(self, clean_db: Session):
        """Test updating non-custom media raises error"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(
            title="External Movie",
            external_id="123",
            external_source="tmdb",
            is_custom=False,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        update_data = MovieCreate(title="Updated Title")

        with pytest.raises(PermissionError):
            media_crud.update_movie(
                db=clean_db, id=movie.id, obj_in=update_data, user_id=user.id
            )

    def test_update_other_user_media_fails(self, clean_db: Session):
        """Test updating another user's media raises error"""
        user1 = user_crud.create(
            db=clean_db,
            username="user1",
            email="user1@example.com",
            password="password123",
        )
        user2 = user_crud.create(
            db=clean_db,
            username="user2",
            email="user2@example.com",
            password="password123",
        )

        movie_data = MovieCreate(title="User1 Movie", is_custom=True)
        movie = media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=user1.id
        )

        update_data = MovieCreate(title="Updated by User2")

        with pytest.raises(PermissionError):
            media_crud.update_movie(
                db=clean_db, id=movie.id, obj_in=update_data, user_id=user2.id
            )

    def test_update_media_tags(self, clean_db: Session):
        """Test updating media with tags"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(
            title="Tagged Movie",
            tags=["action", "sci-fi"],
            is_custom=True,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data, user_id=user.id)
        assert len(movie.tag_associations) == 2

        update_data = MovieCreate(
            title="Tagged Movie",
            description="Test",
            tags=["action", "thriller", "drama"],
        )

        updated = media_crud.update_movie(
            db=clean_db, id=movie.id, obj_in=update_data, user_id=user.id
        )

        assert len(updated.tag_associations) == 3
        tag_names = [assoc.tag.name for assoc in updated.tag_associations]
        assert "action" in tag_names
        assert "thriller" in tag_names
        assert "drama" in tag_names
        assert "sci-fi" not in tag_names

    def test_delete_media(self, clean_db: Session):
        """Test deleting media"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(title="Delete Me", is_custom=True)
        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data, user_id=user.id)

        result = media_crud.delete(db=clean_db, id=movie.id, user_id=user.id)

        assert result is True

        fetched = media_crud.get_by_id(db=clean_db, id=movie.id)
        assert fetched is None

    def test_delete_non_custom_media_fails(self, clean_db: Session):
        """Test deleting non-custom media raises error"""
        user = user_crud.create(
            db=clean_db,
            username="testuser",
            email="test@example.com",
            password="password123",
        )

        movie_data = MovieCreate(
            title="External Movie",
            external_id="123",
            external_source="tmdb",
            is_custom=False,
        )

        movie = media_crud.create_movie(db=clean_db, obj_in=movie_data)

        with pytest.raises(PermissionError):
            media_crud.delete(db=clean_db, id=movie.id, user_id=user.id)

    def test_delete_other_user_media_fails(self, clean_db: Session):
        """Test deleting another user's media raises error"""
        user1 = user_crud.create(
            db=clean_db,
            username="user1",
            email="user1@example.com",
            password="password123",
        )
        user2 = user_crud.create(
            db=clean_db,
            username="user2",
            email="user2@example.com",
            password="password123",
        )

        movie_data = MovieCreate(title="User1 Movie", is_custom=True)
        movie = media_crud.create_movie(
            db=clean_db, obj_in=movie_data, user_id=user1.id
        )

        with pytest.raises(PermissionError):
            media_crud.delete(db=clean_db, id=movie.id, user_id=user2.id)

    def test_delete_nonexistent_media(self, clean_db: Session):
        """Test deleting non-existent media"""
        result = media_crud.delete(db=clean_db, id=999)
        assert result is False
