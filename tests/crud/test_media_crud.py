from datetime import date

import pytest

from app.crud import MediaCRUD
from app.models import MediaTypeEnum
from app.models.game import PlatformEnum
from app.models.media import AnimeSeriesStatusEnum
from app.schemas import (AnimeCreate, AnimeUpdate, BookCreate, GameCreate,
                         MovieCreate, MovieUpdate, SeriesCreate)


@pytest.mark.crud
class TestMediaCRUD:

    def test_create_movie(self, db_session):
        movie_data = MovieCreate(
            title="The Matrix",
            description="A hacker discovers reality is a simulation",
            release_date=date(1999, 3, 31),
            runtime=136,
            director="The Wachowskis",
        )
        movie = MediaCRUD.create_movie(db_session, movie_data)

        assert movie.title == "The Matrix"
        assert movie.runtime == 136
        assert movie.director == "The Wachowskis"
        assert movie.media_type == MediaTypeEnum.MOVIE

    def test_create_series(self, db_session):
        series_data = SeriesCreate(
            title="Breaking Bad",
            description="A chemistry teacher turned meth cook",
            total_episodes=62,
            seasons=5,
            status=AnimeSeriesStatusEnum.FINISHED,
        )
        series = MediaCRUD.create_series(db_session, series_data)

        assert series.title == "Breaking Bad"
        assert series.total_episodes == 62
        assert series.seasons == 5
        assert series.media_type == MediaTypeEnum.SERIES

    def test_create_anime(self, db_session):
        anime_data = AnimeCreate(
            title="Cowboy Bebop",
            description="Space bounty hunters",
            total_episodes=26,
            studio="Sunrise",
            status=AnimeSeriesStatusEnum.FINISHED,
        )
        anime = MediaCRUD.create_anime(db_session, anime_data)

        assert anime.title == "Cowboy Bebop"
        assert anime.studio == "Sunrise"
        assert anime.media_type == MediaTypeEnum.ANIME

    def test_create_book(self, db_session):
        book_data = BookCreate(
            title="Dune",
            description="A desert planet and spice",
            pages=688,
            author="Frank Herbert",
            isbn="978-0441172719",
        )
        book = MediaCRUD.create_book(db_session, book_data)

        assert book.title == "Dune"
        assert book.author == "Frank Herbert"
        assert book.pages == 688
        assert book.media_type == MediaTypeEnum.BOOK

    def test_create_game(self, db_session):
        game_data = GameCreate(
            title="Elden Ring",
            description="A dark fantasy action RPG",
            platform=PlatformEnum.PC,
            developer="FromSoftware",
            publisher="Bandai Namco",
        )
        game = MediaCRUD.create_game(db_session, game_data)

        assert game.title == "Elden Ring"
        assert game.developer == "FromSoftware"
        assert game.platform == PlatformEnum.PC
        assert game.media_type == MediaTypeEnum.GAME

    def test_get_media_by_id(self, db_session):
        movie_data = MovieCreate(title="Test Movie", runtime=120)
        created_movie = MediaCRUD.create_movie(db_session, movie_data)

        fetched_movie = MediaCRUD.get_by_id(
            db_session, created_movie.id, MediaTypeEnum.MOVIE
        )

        assert fetched_movie is not None
        assert fetched_movie.id == created_movie.id
        assert fetched_movie.title == "Test Movie"

    def test_get_all_media(self, db_session):
        MediaCRUD.create_movie(db_session, MovieCreate(title="Movie1", runtime=90))
        MediaCRUD.create_series(db_session, SeriesCreate(title="Series1", seasons=3))
        MediaCRUD.create_anime(
            db_session, AnimeCreate(title="Anime1", studio="Studio1")
        )

        all_media = MediaCRUD.get_all(db_session)

        assert len(all_media) == 3

    def test_get_all_media_filtered_by_type(self, db_session):
        MediaCRUD.create_movie(db_session, MovieCreate(title="Movie1", runtime=90))
        MediaCRUD.create_movie(db_session, MovieCreate(title="Movie2", runtime=100))
        MediaCRUD.create_series(db_session, SeriesCreate(title="Series1", seasons=3))

        movies = MediaCRUD.get_all(db_session, media_type=MediaTypeEnum.MOVIE)

        assert len(movies) == 2
        assert all(m.media_type == MediaTypeEnum.MOVIE for m in movies)

    def test_search_media(self, db_session):
        MediaCRUD.create_movie(
            db_session, MovieCreate(title="The Dark Knight", runtime=152)
        )
        MediaCRUD.create_movie(db_session, MovieCreate(title="Dark City", runtime=100))
        MediaCRUD.create_series(
            db_session, SeriesCreate(title="Breaking Bad", seasons=5)
        )

        results = MediaCRUD.search(db_session, "Dark")

        assert len(results) == 2
        assert all("Dark" in r.title for r in results)

    def test_update_movie(self, db_session):
        movie_data = MovieCreate(title="Original Title", runtime=100)
        movie = MediaCRUD.create_movie(db_session, movie_data)

        update_data = MovieUpdate(runtime=150, director="New Director")
        updated_movie = MediaCRUD.update_movie(db_session, movie.id, update_data)

        assert updated_movie.runtime == 150
        assert updated_movie.director == "New Director"
        assert updated_movie.title == "Original Title"

    def test_update_anime(self, db_session):
        anime_data = AnimeCreate(title="Test Anime", studio="OldStudio")
        anime = MediaCRUD.create_anime(db_session, anime_data)

        update_data = AnimeUpdate(studio="NewStudio", total_episodes=24)
        updated_anime = MediaCRUD.update_anime(db_session, anime.id, update_data)

        assert updated_anime.studio == "NewStudio"
        assert updated_anime.total_episodes == 24

    def test_delete_media(self, db_session):
        movie_data = MovieCreate(title="Delete Me", runtime=90)
        movie = MediaCRUD.create_movie(db_session, movie_data)

        result = MediaCRUD.delete(db_session, movie.id)

        assert result is True
        assert MediaCRUD.get_by_id(db_session, movie.id) is None

    def test_delete_nonexistent_media(self, db_session):
        result = MediaCRUD.delete(db_session, 99999)

        assert result is False

    def test_custom_media_flag(self, db_session):
        movie_data = MovieCreate(title="Custom Movie", runtime=90, is_custom=True)
        movie = MediaCRUD.create_movie(db_session, movie_data)

        assert movie.is_custom is True

    def test_search_with_limit(self, db_session):
        for i in range(30):
            MediaCRUD.create_movie(
                db_session, MovieCreate(title=f"Movie {i}", runtime=90)
            )

        results = MediaCRUD.search(db_session, "Movie", limit=10)

        assert len(results) == 10
