from typing import List, Optional, Type

from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logger import setup_logger
from app.crud.base import CRUDBase
from app.crud.tag import tag_crud
from app.models import MediaTypeEnum
from app.models.anime import Anime
from app.models.book import Book
from app.models.game import Game
from app.models.manga import Manga
from app.models.media import Media
from app.models.movie import Movie
from app.models.series import Series

logger = setup_logger("crud.media")


class CRUDMedia(CRUDBase[Media]):
    """CRUD operations for media with polymorphic support"""

    MODEL_MAP = {
        MediaTypeEnum.MOVIE: Movie,
        MediaTypeEnum.SERIES: Series,
        MediaTypeEnum.ANIME: Anime,
        MediaTypeEnum.MANGA: Manga,
        MediaTypeEnum.BOOK: Book,
        MediaTypeEnum.GAME: Game,
    }

    def _get_model_class(self, media_type: MediaTypeEnum) -> Type[Media]:
        """Get the appropriate model class for media type"""
        return self.MODEL_MAP.get(media_type, Media)

    def get_by_id(
        self, db: Session, *, id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> Optional[Media]:
        """Get media by ID, optionally filtered by type"""
        logger.debug(f"Getting media with id: {id}, type: {media_type}")

        query = db.query(Media).filter(Media.id == id)

        if media_type:
            query = query.filter(Media.media_type == media_type)

        return query.first()

    def get_all(
        self,
        db: Session,
        *,
        media_type: Optional[MediaTypeEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Media]:
        """Get all media, optionally filtered by type"""
        logger.debug(
            f"Getting all media (type: {media_type}, skip: {skip}, limit: {limit})"
        )

        query = db.query(Media)

        if media_type:
            query = query.filter(Media.media_type == media_type)

        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        media_type: Optional[MediaTypeEnum] = None,
        limit: int = 100,
    ) -> List[Media]:
        """Search media by title or description"""
        logger.info(f"Searching media for: {query} (type: {media_type})")

        search_query = db.query(Media).filter(
            or_(Media.title.ilike(f"%{query}%"), Media.description.ilike(f"%{query}%"))
        )

        if media_type:
            search_query = search_query.filter(Media.media_type == media_type)

        results = search_query.limit(limit).all()
        logger.debug(f"Search returned {len(results)} results")
        return results

    def _create_with_tags(
        self,
        db: Session,
        *,
        model_class: Type[Media],
        obj_in: BaseModel,
        media_type: MediaTypeEnum,
    ) -> Media:
        """Create media with automatic tag handling"""
        # Extract tags from schema if present
        obj_data = obj_in.model_dump(exclude_unset=True)
        tags = obj_data.pop("tags", None)

        # Create media object
        logger.info(f"Creating {media_type.value}: {obj_data.get('title', 'Unknown')}")
        media = model_class(**obj_data)
        db.add(media)
        db.flush()  # Get the ID without committing

        # Add tags if present
        if tags:
            tag_crud.add_tags_to_media(
                db, media_id=media.id, media_type=media_type, tag_names=tags
            )

        db.commit()
        db.refresh(media)

        logger.debug(f"Created {media_type.value} with id: {media.id}")
        return media

    def create_movie(self, db: Session, *, obj_in: BaseModel) -> Movie:
        """Create a movie"""
        return self._create_with_tags(
            db, model_class=Movie, obj_in=obj_in, media_type=MediaTypeEnum.MOVIE
        )

    def create_series(self, db: Session, *, obj_in: BaseModel) -> Series:
        """Create a series"""
        return self._create_with_tags(
            db, model_class=Series, obj_in=obj_in, media_type=MediaTypeEnum.SERIES
        )

    def create_anime(self, db: Session, *, obj_in: BaseModel) -> Anime:
        """Create an anime"""
        return self._create_with_tags(
            db, model_class=Anime, obj_in=obj_in, media_type=MediaTypeEnum.ANIME
        )

    def create_manga(self, db: Session, *, obj_in: BaseModel) -> Manga:
        """Create a manga"""
        return self._create_with_tags(
            db, model_class=Manga, obj_in=obj_in, media_type=MediaTypeEnum.MANGA
        )

    def create_book(self, db: Session, *, obj_in: BaseModel) -> Book:
        """Create a book"""
        return self._create_with_tags(
            db, model_class=Book, obj_in=obj_in, media_type=MediaTypeEnum.BOOK
        )

    def create_game(self, db: Session, *, obj_in: BaseModel) -> Game:
        """Create a game"""
        return self._create_with_tags(
            db, model_class=Game, obj_in=obj_in, media_type=MediaTypeEnum.GAME
        )

    def _update_with_tags(
        self, db: Session, *, media: Media, obj_in: BaseModel
    ) -> Media:
        """Update media with automatic tag handling"""
        logger.info(f"Updating {media.media_type.value} with id: {media.id}")

        # Extract tags from schema if present
        obj_data = obj_in.model_dump(exclude_unset=True)
        tags = obj_data.pop("tags", None)

        # Update media fields
        for field, value in obj_data.items():
            if value is not None:
                setattr(media, field, value)

        db.add(media)
        db.flush()

        # Update tags if present
        if tags is not None:  # Allow empty list to clear tags
            tag_crud.update_media_tags(
                db, media_id=media.id, media_type=media.media_type, tag_names=tags
            )

        db.commit()
        db.refresh(media)

        logger.debug(f"Updated {media.media_type.value} with id: {media.id}")
        return media

    def update_movie(
        self, db: Session, *, id: int, obj_in: BaseModel
    ) -> Optional[Movie]:
        """Update a movie"""
        movie = self.get_by_id(db, id=id, media_type=MediaTypeEnum.MOVIE)
        if not movie:
            logger.warning(f"Movie not found with id: {id}")
            return None
        return self._update_with_tags(db, media=movie, obj_in=obj_in)

    def update_series(
        self, db: Session, *, id: int, obj_in: BaseModel
    ) -> Optional[Series]:
        """Update a series"""
        series = self.get_by_id(db, id=id, media_type=MediaTypeEnum.SERIES)
        if not series:
            logger.warning(f"Series not found with id: {id}")
            return None
        return self._update_with_tags(db, media=series, obj_in=obj_in)

    def update_anime(
        self, db: Session, *, id: int, obj_in: BaseModel
    ) -> Optional[Anime]:
        """Update an anime"""
        anime = self.get_by_id(db, id=id, media_type=MediaTypeEnum.ANIME)
        if not anime:
            logger.warning(f"Anime not found with id: {id}")
            return None
        return self._update_with_tags(db, media=anime, obj_in=obj_in)

    def update_manga(
        self, db: Session, *, id: int, obj_in: BaseModel
    ) -> Optional[Manga]:
        """Update a manga"""
        manga = self.get_by_id(db, id=id, media_type=MediaTypeEnum.MANGA)
        if not manga:
            logger.warning(f"Manga not found with id: {id}")
            return None
        return self._update_with_tags(db, media=manga, obj_in=obj_in)

    def update_book(self, db: Session, *, id: int, obj_in: BaseModel) -> Optional[Book]:
        """Update a book"""
        book = self.get_by_id(db, id=id, media_type=MediaTypeEnum.BOOK)
        if not book:
            logger.warning(f"Book not found with id: {id}")
            return None
        return self._update_with_tags(db, media=book, obj_in=obj_in)

    def update_game(self, db: Session, *, id: int, obj_in: BaseModel) -> Optional[Game]:
        """Update a game"""
        game = self.get_by_id(db, id=id, media_type=MediaTypeEnum.GAME)
        if not game:
            logger.warning(f"Game not found with id: {id}")
            return None
        return self._update_with_tags(db, media=game, obj_in=obj_in)

    def delete(self, db: Session, *, id: int) -> bool:
        """Delete media by ID"""
        logger.info(f"Deleting media with id: {id}")

        media = self.get_by_id(db, id=id)
        if not media:
            logger.warning(f"Media not found with id: {id}")
            return False

        # Tags will be deleted automatically via cascade
        db.delete(media)
        db.commit()

        logger.debug(f"Deleted media with id: {id}")
        return True


media_crud = CRUDMedia(Media)
