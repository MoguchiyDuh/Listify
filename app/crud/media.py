from typing import List, Optional, Type

from app.core import setup_logger
from app.models import Anime, Book, Game, Media, MediaTypeEnum, Movie, Series
from app.schemas import (AnimeCreate, AnimeUpdate, BookCreate, BookUpdate,
                         GameCreate, GameUpdate, MediaUpdate, MovieCreate,
                         MovieUpdate, SeriesCreate, SeriesUpdate)
from sqlalchemy.orm import Session

logger = setup_logger(__name__)

# Type mapping for polymorphic models
MEDIA_TYPE_MAP: dict[MediaTypeEnum, Type[Media]] = {
    MediaTypeEnum.MOVIE: Movie,
    MediaTypeEnum.SERIES: Series,
    MediaTypeEnum.ANIME: Anime,
    MediaTypeEnum.BOOK: Book,
    MediaTypeEnum.GAME: Game,
}


class MediaCRUD:
    @staticmethod
    def create_movie(db: Session, movie_data: MovieCreate) -> Movie:
        logger.debug(f"Creating movie: {movie_data.title}")

        movie = Movie(media_type=MediaTypeEnum.MOVIE, **movie_data.model_dump())

        db.add(movie)
        db.commit()
        db.refresh(movie)

        logger.debug(f"Movie created successfully: {movie.id}")
        return movie

    @staticmethod
    def create_series(db: Session, series_data: SeriesCreate) -> Series:
        logger.debug(f"Creating series: {series_data.title}")

        series = Series(media_type=MediaTypeEnum.SERIES, **series_data.model_dump())

        db.add(series)
        db.commit()
        db.refresh(series)

        logger.debug(f"Series created successfully: {series.id}")
        return series

    @staticmethod
    def create_anime(db: Session, anime_data: AnimeCreate) -> Anime:
        logger.debug(f"Creating anime: {anime_data.title}")

        anime = Anime(media_type=MediaTypeEnum.ANIME, **anime_data.model_dump())

        db.add(anime)
        db.commit()
        db.refresh(anime)

        logger.debug(f"Anime created successfully: {anime.id}")
        return anime

    @staticmethod
    def create_book(db: Session, book_data: BookCreate) -> Book:
        logger.debug(f"Creating book: {book_data.title}")

        book = Book(media_type=MediaTypeEnum.BOOK, **book_data.model_dump())

        db.add(book)
        db.commit()
        db.refresh(book)

        logger.debug(f"Book created successfully: {book.id}")
        return book

    @staticmethod
    def create_game(db: Session, game_data: GameCreate) -> Game:
        logger.debug(f"Creating game: {game_data.title}")

        game = Game(media_type=MediaTypeEnum.GAME, **game_data.model_dump())

        db.add(game)
        db.commit()
        db.refresh(game)

        logger.debug(f"Game created successfully: {game.id}")
        return game

    @staticmethod
    def get_by_id(
        db: Session, media_id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> Optional[Media]:
        logger.debug(f"Fetching media by ID: {media_id}, type: {media_type}")

        query = db.query(Media).filter(Media.id == media_id)

        if media_type:
            model_class = MEDIA_TYPE_MAP.get(media_type, Media)
            query = db.query(model_class).filter(model_class.id == media_id)

        media = query.first()

        if media:
            logger.debug(f"Media found: {media.title}")
        else:
            logger.debug(f"Media not found: {media_id}")

        return media

    @staticmethod
    def get_all(
        db: Session,
        media_type: Optional[MediaTypeEnum] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> List[Media]:
        logger.debug(
            f"Fetching media list - type: {media_type}, skip: {skip}, limit: {limit}, search: {search}"
        )

        if media_type:
            model_class = MEDIA_TYPE_MAP.get(media_type, Media)
            query = db.query(model_class)
        else:
            query = db.query(Media)

        if search:
            query = query.filter(Media.title.ilike(f"%{search}%"))

        media_list = query.offset(skip).limit(limit).all()

        logger.debug(f"Found {len(media_list)} media items")
        return media_list

    @staticmethod
    def update_movie(
        db: Session, movie_id: int, movie_data: MovieUpdate
    ) -> Optional[Movie]:
        logger.debug(f"Updating movie: {movie_id}")

        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            logger.debug(f"Movie not found for update: {movie_id}")
            return None

        update_data = movie_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(movie, field, value)

        db.commit()
        db.refresh(movie)

        logger.debug(f"Movie updated successfully: {movie.id}")
        return movie

    @staticmethod
    def update_series(
        db: Session, series_id: int, series_data: SeriesUpdate
    ) -> Optional[Series]:
        logger.debug(f"Updating series: {series_id}")

        series = db.query(Series).filter(Series.id == series_id).first()
        if not series:
            logger.debug(f"Series not found for update: {series_id}")
            return None

        update_data = series_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(series, field, value)

        db.commit()
        db.refresh(series)

        logger.debug(f"Series updated successfully: {series.id}")
        return series

    @staticmethod
    def update_anime(
        db: Session, anime_id: int, anime_data: AnimeUpdate
    ) -> Optional[Anime]:
        logger.debug(f"Updating anime: {anime_id}")

        anime = db.query(Anime).filter(Anime.id == anime_id).first()
        if not anime:
            logger.debug(f"Anime not found for update: {anime_id}")
            return None

        update_data = anime_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(anime, field, value)

        db.commit()
        db.refresh(anime)

        logger.debug(f"Anime updated successfully: {anime.id}")
        return anime

    @staticmethod
    def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        logger.debug(f"Updating book: {book_id}")

        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.debug(f"Book not found for update: {book_id}")
            return None

        update_data = book_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(book, field, value)

        db.commit()
        db.refresh(book)

        logger.debug(f"Book updated successfully: {book.id}")
        return book

    @staticmethod
    def update_game(db: Session, game_id: int, game_data: GameUpdate) -> Optional[Game]:
        logger.debug(f"Updating game: {game_id}")

        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            logger.debug(f"Game not found for update: {game_id}")
            return None

        update_data = game_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(game, field, value)

        db.commit()
        db.refresh(game)

        logger.debug(f"Game updated successfully: {game.id}")
        return game

    @staticmethod
    def update(db: Session, media_id: int, media_data: MediaUpdate) -> Optional[Media]:
        logger.debug(f"Updating generic media: {media_id}")

        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            logger.debug(f"Media not found for update: {media_id}")
            return None

        update_data = media_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(media, field, value)

        db.commit()
        db.refresh(media)

        logger.debug(f"Media updated successfully: {media.id}")
        return media

    @staticmethod
    def delete(db: Session, media_id: int) -> bool:
        logger.debug(f"Deleting media: {media_id}")

        media = db.query(Media).filter(Media.id == media_id).first()
        if not media:
            logger.debug(f"Media not found for deletion: {media_id}")
            return False

        db.delete(media)
        db.commit()

        logger.debug(f"Media deleted successfully: {media_id}")
        return True

    @staticmethod
    def search(
        db: Session,
        query: str,
        media_type: Optional[MediaTypeEnum] = None,
        limit: int = 20,
    ) -> List[Media]:
        logger.debug(
            f"Searching media - query: {query}, type: {media_type}, limit: {limit}"
        )

        if media_type:
            model_class = MEDIA_TYPE_MAP.get(media_type, Media)
            search_query = db.query(model_class)
        else:
            search_query = db.query(Media)

        search_query = search_query.filter(Media.title.ilike(f"%{query}%"))
        results = search_query.limit(limit).all()

        logger.debug(f"Found {len(results)} search results")
        return results
