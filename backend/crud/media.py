from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.cache import cache
from core.exceptions import AlreadyExists, PermissionDenied
from models import (Anime, Book, Game, Manga, Media, MediaTag, MediaTypeEnum,
                    Movie, Series, Tag, Tracking)

from .base import CRUDBase, logger
from .tag import tag_crud

logger = logger.bind(module="media")


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

    async def get_by_id(
        self, db: AsyncSession, *, id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> Optional[Media]:
        """Get media by ID, optionally filtered by type"""
        logger.debug(f"Getting media with id: {id}, type: {media_type}")

        stmt = (
            select(Media)
            .options(selectinload(Media.tag_associations).selectinload(MediaTag.tag))
            .filter(Media.id == id)
        )

        if media_type:
            stmt = stmt.filter(Media.media_type == media_type)

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        media_type: Optional[MediaTypeEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Media]:
        """Get all media, optionally filtered by type"""
        logger.debug(
            f"Getting all media (type: {media_type}, skip: {skip}, limit: {limit})"
        )

        stmt = select(Media).options(
            selectinload(Media.tag_associations).selectinload(MediaTag.tag)
        )

        if media_type:
            stmt = stmt.filter(Media.media_type == media_type)

        result = await db.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        media_type: Optional[MediaTypeEnum] = None,
        limit: int = 100,
    ) -> List[Media]:
        """Search media by title or description"""
        logger.info(f"Searching media for: {query} (type: {media_type})")

        stmt = (
            select(Media)
            .options(selectinload(Media.tag_associations).selectinload(MediaTag.tag))
            .filter(
                or_(
                    Media.title.ilike(f"%{query}%"),
                    Media.description.ilike(f"%{query}%"),
                )
            )
        )

        if media_type:
            stmt = stmt.filter(Media.media_type == media_type)

        result = await db.execute(stmt.limit(limit))
        results = list(result.scalars().all())
        logger.debug(f"Search returned {len(results)} results")
        return results

    async def get_by_external_id(
        self,
        db: AsyncSession,
        *,
        external_id: str,
        external_source: str,
        media_type: MediaTypeEnum,
    ) -> Optional[Media]:
        """Get media by external ID and source"""
        logger.debug(
            f"Checking for existing media: external_id={external_id}, "
            f"source={external_source}, type={media_type}"
        )
        stmt = select(Media).filter(
            Media.external_id == external_id,
            Media.external_source == external_source,
            Media.media_type == media_type,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _create_with_tags(
        self,
        db: AsyncSession,
        *,
        model_class: Type[Media],
        obj_in: BaseModel,
        media_type: MediaTypeEnum,
        user_id: Optional[int] = None,
    ) -> Media:
        """Create media with automatic tag handling"""
        try:
            obj_data = obj_in.model_dump(exclude_unset=True)
            tags = obj_data.pop("tags", None)

            external_id = obj_data.get("external_id")
            external_source = obj_data.get("external_source")

            if external_id and external_source:
                existing_media = await self.get_by_external_id(
                    db,
                    external_id=external_id,
                    external_source=external_source,
                    media_type=media_type,
                )
                if existing_media:
                    logger.info(
                        f"Found existing {media_type.value} with external_id={external_id}, "
                        f"returning existing media with id: {existing_media.id}"
                    )
                    return existing_media

            is_custom = obj_data.get("is_custom", False)
            if is_custom and user_id:
                # Duplicate check for custom media
                stmt = select(Media).filter(
                    Media.is_custom == True,
                    Media.created_by_id == user_id,
                    Media.media_type == media_type,
                    Media.title.ilike(obj_data["title"]),
                )

                release_date = obj_data.get("release_date")
                if release_date:
                    stmt = stmt.filter(Media.release_date == release_date)
                else:
                    stmt = stmt.filter(Media.release_date.is_(None))

                result = await db.execute(stmt)
                if result.scalar_one_or_none():
                    logger.warning(
                        f"Custom media '{obj_data['title']}' already exists for user {user_id}"
                    )
                    raise AlreadyExists("Custom media", obj_data["title"])

                obj_data["created_by_id"] = user_id

            logger.info(
                f"Creating {media_type.value}: {obj_data.get('title', 'Unknown')}"
            )
            media = model_class(**obj_data)
            db.add(media)
            await db.flush()  # Get the ID without committing

            if tags:
                await tag_crud.add_tags_to_media(
                    db, media_id=media.id, media_type=media_type, tag_names=tags
                )

            await db.commit()

            await db.refresh(media)

            # Invalidate search cache for this source
            if external_source:
                await cache.clear_pattern(f"api:{external_source}:search:*")

            stmt = (
                select(model_class)
                .options(
                    selectinload(Media.tag_associations).selectinload(MediaTag.tag)
                )
                .where(Media.id == media.id)
            )
            result = await db.execute(stmt)
            media = result.scalar_one()

            logger.debug(f"Created {media_type.value} with id: {media.id}")
            return media

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating {media_type.value}: {str(e)}")
            raise

    async def create_movie(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Movie:
        """Create a movie"""
        return await self._create_with_tags(
            db,
            model_class=Movie,
            obj_in=obj_in,
            media_type=MediaTypeEnum.MOVIE,
            user_id=user_id,
        )

    async def create_series(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Series:
        """Create a series"""
        return await self._create_with_tags(
            db,
            model_class=Series,
            obj_in=obj_in,
            media_type=MediaTypeEnum.SERIES,
            user_id=user_id,
        )

    async def create_anime(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Anime:
        """Create an anime"""
        return await self._create_with_tags(
            db,
            model_class=Anime,
            obj_in=obj_in,
            media_type=MediaTypeEnum.ANIME,
            user_id=user_id,
        )

    async def create_manga(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Manga:
        """Create a manga"""
        return await self._create_with_tags(
            db,
            model_class=Manga,
            obj_in=obj_in,
            media_type=MediaTypeEnum.MANGA,
            user_id=user_id,
        )

    async def create_book(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Book:
        """Create a book"""
        return await self._create_with_tags(
            db,
            model_class=Book,
            obj_in=obj_in,
            media_type=MediaTypeEnum.BOOK,
            user_id=user_id,
        )

    async def create_game(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: Optional[int] = None
    ) -> Game:
        """Create a game"""
        return await self._create_with_tags(
            db,
            model_class=Game,
            obj_in=obj_in,
            media_type=MediaTypeEnum.GAME,
            user_id=user_id,
        )

    def can_modify_media(self, media: Media, user_id: int) -> bool:
        """Check if user can modify this media"""
        if not media.is_custom:
            return False
        return media.created_by_id == user_id

    async def _update_with_tags(
        self,
        db: AsyncSession,
        *,
        media: Media,
        obj_in: BaseModel,  # More specific type hint
        user_id: Optional[int] = None,
    ) -> Media:
        """Update media with automatic tag handling"""
        media_id = media.id
        media_type = media.media_type

        try:
            logger.info(f"Updating {media_type.value} with id: {media_id}")

            if user_id and not self.can_modify_media(media, user_id):
                logger.warning(f"User {user_id} not allowed to modify media {media_id}")
                raise PermissionDenied("Cannot modify this media")

            obj_data = obj_in.model_dump(
                exclude_unset=True, exclude_none=True
            )  # Added exclude_none
            tags = obj_data.pop("tags", None)

            for field, value in obj_data.items():
                if hasattr(media, field):  # Safety check
                    setattr(media, field, value)
                else:
                    logger.warning(
                        f"Field {field} does not exist on {type(media).__name__}"
                    )

            db.add(media)
            await db.flush()

            if tags is not None:
                await tag_crud.update_media_tags(
                    db, media_id=media_id, media_type=media_type, tag_names=tags
                )

            await db.commit()

            # Invalidate details cache for this item
            if media.external_id and media.external_source:
                # We don't know the exact endpoint used, so clear patterns
                await cache.clear_pattern(f"api:{media.external_source}:*{media.external_id}*")

            stmt = (
                select(type(media))
                .options(
                    selectinload(Media.tag_associations).selectinload(MediaTag.tag)
                )
                .where(Media.id == media_id)
            )
            result = await db.execute(stmt)
            updated_media = result.scalar_one()

            logger.debug(
                f"Updated {media_type.value} with id: {updated_media.id}"
            )
            return updated_media

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating media {media_id}: {str(e)}")
            raise

    async def update_movie(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Movie]:
        """Update a movie"""
        movie = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.MOVIE)
        if not movie:
            logger.warning(f"Movie not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=movie, obj_in=obj_in, user_id=user_id
        )

    async def update_series(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Series]:
        """Update a series"""
        series = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.SERIES)
        if not series:
            logger.warning(f"Series not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=series, obj_in=obj_in, user_id=user_id
        )

    async def update_anime(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Anime]:
        """Update an anime"""
        anime = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.ANIME)
        if not anime:
            logger.warning(f"Anime not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=anime, obj_in=obj_in, user_id=user_id
        )

    async def update_manga(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Manga]:
        """Update a manga"""
        manga = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.MANGA)
        if not manga:
            logger.warning(f"Manga not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=manga, obj_in=obj_in, user_id=user_id
        )

    async def update_book(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Book]:
        """Update a book"""
        book = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.BOOK)
        if not book:
            logger.warning(f"Book not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=book, obj_in=obj_in, user_id=user_id
        )

    async def update_game(
        self,
        db: AsyncSession,
        *,
        id: int,
        obj_in: BaseModel,
        user_id: Optional[int] = None,
    ) -> Optional[Game]:
        """Update a game"""
        game = await self.get_by_id(db, id=id, media_type=MediaTypeEnum.GAME)
        if not game:
            logger.warning(f"Game not found with id: {id}")
            return None
        return await self._update_with_tags(
            db, media=game, obj_in=obj_in, user_id=user_id
        )

    async def delete(
        self, db: AsyncSession, *, id: int, user_id: Optional[int] = None, commit: bool = True
    ) -> bool:
        """Delete media by ID"""
        try:
            logger.info(f"Attempting to delete media with id: {id}")

            media = await self.get_by_id(db, id=id)
            if not media:
                logger.warning(f"Media not found with id: {id}")
                return False

            if user_id and not self.can_modify_media(media, user_id):
                logger.warning(f"User {user_id} not allowed to delete media {id}")
                raise PermissionDenied("Cannot delete this media")

            # File cleanup logic
            if media.cover_image_url and media.cover_image_url.startswith("/static/images/"):
                try:
                    # Resolve path relative to project root
                    base_path = Path(__file__).resolve().parent.parent.parent
                    relative_path = media.cover_image_url.lstrip("/")
                    file_path = base_path / relative_path

                    if file_path.is_file():
                        logger.info(f"Deleting local image file: {file_path}")
                        file_path.unlink(missing_ok=True)
                except (PermissionError, OSError) as e:
                    # Log warning but don't block DB deletion
                    logger.warning(f"Could not delete file {media.cover_image_url} (permission/OS error): {str(e)}")
                except Exception as e:
                    # Log error but don't block DB deletion
                    logger.error(f"Unexpected error deleting file {media.cover_image_url}: {str(e)}")

            external_id = media.external_id
            external_source = media.external_source

            await db.delete(media)
            if commit:
                await db.commit()

            # Invalidate cache
            if external_id and external_source:
                await cache.clear_pattern(f"api:{external_source}:*{external_id}*")
                await cache.clear_pattern(f"api:{external_source}:search:*")

            logger.info(f"Successfully deleted media with id: {id}")
            return True

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error deleting media {id}: {str(e)}")
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Unexpected error deleting media {id}: {str(e)}")
            raise

    async def cleanup_orphaned_media(self, db: AsyncSession) -> int:
        """
        Delete media that are not referenced by any tracking entries.
        Includes both API-sourced and custom media.
        """
        logger.info("Starting orphaned media cleanup")

        # Find media IDs that are NOT present in the tracking table
        # We use a subquery for all media_ids in tracking
        tracking_stmt = select(Tracking.media_id)
        stmt = select(Media.id).where(Media.id.not_in(tracking_stmt))
        
        result = await db.execute(stmt)
        orphaned_ids = list(result.scalars().all())

        count = 0
        if orphaned_ids:
            logger.info(f"Found {len(orphaned_ids)} orphaned media items to clean up")
            for media_id in orphaned_ids:
                # Using self.delete ensures file cleanup and cache invalidation
                if await self.delete(db, id=media_id, commit=False):
                    count += 1
            
            await db.commit()
            logger.info(f"Successfully cleaned up {count} orphaned media items")
        else:
            logger.info("No orphaned media items found")

        return count


media_crud = CRUDMedia(Media)
