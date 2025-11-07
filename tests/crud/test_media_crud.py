from datetime import date

import pytest

from app.crud import media_crud, tag_crud
from app.models import (AgeRatingEnum, MediaStatusEnum, MediaTypeEnum,
                        PlatformEnum)
from app.schemas.anime import AnimeCreate, AnimeUpdate
from app.schemas.book import BookCreate
from app.schemas.game import GameCreate
from app.schemas.movie import MovieCreate, MovieUpdate
from app.schemas.series import SeriesCreate


@pytest.mark.crud
class TestMediaCRUD:
    """Tests for media CRUD operations"""

    def test_create_movie(self, db_session):
        """Test creating a movie"""
        movie_data = MovieCreate(
            title="The Matrix",
            description="A hacker discovers reality is a simulation",
            release_date=date(1999, 3, 31),
            runtime=136,
            tags=["Sci-Fi", "Action"],
        )

        movie = media_crud.create_movie(db_session, obj_in=movie_data)

        assert movie.id is not None
        assert movie.title == "The Matrix"
        assert movie.runtime == 136
        assert movie.media_type == MediaTypeEnum.MOVIE

        # Verify tags were created
        tags = tag_crud.get_tags_for_media(db_session, media_id=movie.id)
        tag_names = {t.name for t in tags}
        assert "Sci-Fi" in tag_names
        assert "Action" in tag_names

    def test_create_anime(self, db_session):
        """Test creating an anime"""
        anime_data = AnimeCreate(
            title="Cowboy Bebop",
            original_title="カウボーイビバップ",
            description="Space bounty hunters",
            total_episodes=26,
            studios=["Sunrise"],
            status=MediaStatusEnum.FINISHED,
            age_rating=AgeRatingEnum.PG_13,
            tags=["Space", "Action", "Jazz"],
        )

        anime = media_crud.create_anime(db_session, obj_in=anime_data)

        assert anime.id is not None
        assert anime.title == "Cowboy Bebop"
        assert anime.total_episodes == 26
        assert anime.media_type == MediaTypeEnum.ANIME
        assert len(anime.studios) == 1

        # Verify tags
        tags = tag_crud.get_tags_for_media(db_session, media_id=anime.id)
        assert len(tags) == 3

    def test_create_game(self, db_session):
        """Test creating a game"""
        game_data = GameCreate(
            title="Elden Ring",
            description="A dark fantasy action RPG",
            platforms=[PlatformEnum.PC, PlatformEnum.PS5],
            developer="FromSoftware",
            publisher="Bandai Namco",
            tags=["RPG", "Dark Fantasy", "Open World"],
        )

        game = media_crud.create_game(db_session, obj_in=game_data)

        assert game.id is not None
        assert game.title == "Elden Ring"
        assert game.media_type == MediaTypeEnum.GAME
        assert len(game.platforms) == 2

        # Verify tags
        tags = tag_crud.get_tags_for_media(db_session, media_id=game.id)
        assert len(tags) == 3

    def test_create_movie_without_tags(self, db_session):
        """Test creating a movie without tags"""
        movie_data = MovieCreate(title="Simple Movie", runtime=90)

        movie = media_crud.create_movie(db_session, obj_in=movie_data)

        assert movie.id is not None

        # Verify no tags were created
        tags = tag_crud.get_tags_for_media(db_session, media_id=movie.id)
        assert len(tags) == 0

    def test_get_by_id(self, db_session, sample_movie):
        """Test getting media by ID"""
        movie = media_crud.get_by_id(db_session, id=sample_movie.id)

        assert movie is not None
        assert movie.id == sample_movie.id
        assert movie.title == sample_movie.title

    def test_get_by_id_with_type_filter(self, db_session, sample_movie):
        """Test getting media by ID with type filter"""
        # Should find with correct type
        movie = media_crud.get_by_id(
            db_session, id=sample_movie.id, media_type=MediaTypeEnum.MOVIE
        )
        assert movie is not None

        # Should not find with wrong type
        anime = media_crud.get_by_id(
            db_session, id=sample_movie.id, media_type=MediaTypeEnum.ANIME
        )
        assert anime is None

    def test_get_all(self, db_session, sample_movie, sample_anime, sample_game):
        """Test getting all media"""
        media_list = media_crud.get_all(db_session)

        assert len(media_list) >= 3

        media_ids = {m.id for m in media_list}
        assert sample_movie.id in media_ids
        assert sample_anime.id in media_ids
        assert sample_game.id in media_ids

    def test_get_all_filtered_by_type(self, db_session, sample_movie, sample_anime):
        """Test getting media filtered by type"""
        movies = media_crud.get_all(db_session, media_type=MediaTypeEnum.MOVIE)

        assert all(m.media_type == MediaTypeEnum.MOVIE for m in movies)
        assert sample_movie.id in {m.id for m in movies}
        assert sample_anime.id not in {m.id for m in movies}

    def test_search(self, db_session):
        """Test searching media"""
        # Create test movies
        media_crud.create_movie(
            db_session, obj_in=MovieCreate(title="The Dark Knight", runtime=152)
        )
        media_crud.create_movie(
            db_session, obj_in=MovieCreate(title="Dark City", runtime=100)
        )
        media_crud.create_movie(
            db_session, obj_in=MovieCreate(title="Bright Future", runtime=110)
        )

        # Search for "Dark"
        results = media_crud.search(db_session, query="Dark")

        assert len(results) == 2
        titles = {m.title for m in results}
        assert "The Dark Knight" in titles
        assert "Dark City" in titles

    def test_search_filtered_by_type(self, db_session, sample_movie, sample_anime):
        """Test searching media filtered by type"""
        results = media_crud.search(
            db_session, query="Test", media_type=MediaTypeEnum.MOVIE
        )

        assert all(m.media_type == MediaTypeEnum.MOVIE for m in results)
        assert sample_movie.id in {m.id for m in results}
        assert sample_anime.id not in {m.id for m in results}

    def test_update_movie(self, db_session, sample_movie):
        """Test updating a movie"""
        update_data = MovieUpdate(runtime=150, description="Updated description")

        updated_movie = media_crud.update_movie(
            db_session, id=sample_movie.id, obj_in=update_data
        )

        assert updated_movie is not None
        assert updated_movie.runtime == 150
        assert updated_movie.description == "Updated description"
        assert updated_movie.title == sample_movie.title  # Unchanged

    def test_update_movie_with_tags(self, db_session, sample_movie):
        """Test updating a movie with new tags"""
        update_data = MovieUpdate(tags=["Drama", "Thriller"])

        updated_movie = media_crud.update_movie(
            db_session, id=sample_movie.id, obj_in=update_data
        )

        assert updated_movie is not None

        # Verify tags were updated
        tags = tag_crud.get_tags_for_media(db_session, media_id=updated_movie.id)
        tag_names = {t.name for t in tags}

        assert "Drama" in tag_names
        assert "Thriller" in tag_names
        assert "Action" not in tag_names  # Old tag removed

    def test_update_anime(self, db_session, sample_anime):
        """Test updating an anime"""
        update_data = AnimeUpdate(total_episodes=24, studios=["New Studio"])

        updated_anime = media_crud.update_anime(
            db_session, id=sample_anime.id, obj_in=update_data
        )

        assert updated_anime is not None
        assert updated_anime.total_episodes == 24
        assert updated_anime.studios == ["New Studio"]

    def test_update_nonexistent_movie(self, db_session):
        """Test updating a non-existent movie"""
        update_data = MovieUpdate(runtime=100)

        result = media_crud.update_movie(db_session, id=99999, obj_in=update_data)

        assert result is None

    def test_delete_media(self, db_session, sample_movie):
        """Test deleting media"""
        movie_id = sample_movie.id

        result = media_crud.delete(db_session, id=movie_id)

        assert result is True

        # Verify media is deleted
        movie = media_crud.get_by_id(db_session, id=movie_id)
        assert movie is None

        # Verify tags associations are also deleted (cascade)
        tags = tag_crud.get_tags_for_media(db_session, media_id=movie_id)
        assert len(tags) == 0

    def test_delete_nonexistent_media(self, db_session):
        """Test deleting non-existent media"""
        result = media_crud.delete(db_session, id=99999)

        assert result is False

    def test_create_with_custom_flag(self, db_session):
        """Test creating custom media entry"""
        movie_data = MovieCreate(title="My Custom Movie", runtime=90, is_custom=True)

        movie = media_crud.create_movie(db_session, obj_in=movie_data)

        assert movie.is_custom is True

    def test_pagination(self, db_session):
        """Test pagination of media list"""
        # Create 30 movies
        for i in range(30):
            media_crud.create_movie(
                db_session, obj_in=MovieCreate(title=f"Movie {i}", runtime=90)
            )

        # Get first page
        page1 = media_crud.get_all(db_session, skip=0, limit=10)
        assert len(page1) == 10

        # Get second page
        page2 = media_crud.get_all(db_session, skip=10, limit=10)
        assert len(page2) == 10

        # Verify no overlap
        page1_ids = {m.id for m in page1}
        page2_ids = {m.id for m in page2}
        assert len(page1_ids & page2_ids) == 0
