from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.exceptions import AlreadyExists
from models import Media, MediaTag, MediaTypeEnum, Tracking, TrackingStatusEnum

from .base import CRUDBase, logger

logger = logger.getChild("tracking")


class CRUDTracking(CRUDBase[Tracking]):
    """CRUD operations for tracking"""

    async def get_by_user_and_media(
        self, db: AsyncSession, *, user_id: int, media_id: int
    ) -> Optional[Tracking]:
        """Get tracking entry for user and media"""
        logger.debug(f"Getting tracking for user_id: {user_id}, media_id: {media_id}")
        stmt = (
            select(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(and_(Tracking.user_id == user_id, Tracking.media_id == media_id))
        )
        result = await db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        status: Optional[TrackingStatusEnum] = None,
        media_type: Optional[MediaTypeEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tracking]:
        """Get all tracking entries for a user, optionally filtered"""
        logger.debug(
            f"Getting tracking for user_id: {user_id} "
            f"(status: {status}, media_type: {media_type}, skip: {skip}, limit: {limit})"
        )

        stmt = (
            select(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(Tracking.user_id == user_id)
        )

        if status:
            stmt = stmt.filter(Tracking.status == status)

        if media_type:
            stmt = stmt.filter(Tracking.media_type == media_type)

        result = await db.execute(stmt.offset(skip).limit(limit))
        return list(result.unique().scalars().all())

    async def get_favorites(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        media_type: Optional[MediaTypeEnum] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tracking]:
        """Get user's favorite media"""
        logger.debug(
            f"Getting favorites for user_id: {user_id} (media_type: {media_type})"
        )

        stmt = (
            select(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(and_(Tracking.user_id == user_id, Tracking.favorite.is_(True)))
        )

        if media_type:
            stmt = stmt.filter(Tracking.media_type == media_type)

        result = await db.execute(stmt.offset(skip).limit(limit))
        return list(result.unique().scalars().all())

    async def create(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: int
    ) -> Tracking:
        """Create tracking entry"""
        logger.info(f"Creating tracking for user_id: {user_id}")

        obj_data = obj_in.model_dump(exclude_unset=True)
        obj_data["user_id"] = user_id

        # Check if tracking already exists
        existing = await self.get_by_user_and_media(
            db, user_id=user_id, media_id=obj_data["media_id"]
        )

        if existing:
            logger.warning(
                f"Tracking already exists for user_id: {user_id}, "
                f"media_id: {obj_data['media_id']}"
            )
            raise AlreadyExists("Tracking entry", str(obj_data['media_id']))

        tracking = Tracking(**obj_data)
        db.add(tracking)
        await db.commit()

        # Re-query with eager loading
        stmt = (
            select(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(Tracking.id == tracking.id)
        )
        result = await db.execute(stmt)
        tracking = result.unique().scalar_one()

        logger.debug(f"Created tracking with id: {tracking.id}")
        return tracking

    async def update(
        self, db: AsyncSession, *, tracking: Tracking, obj_in: BaseModel
    ) -> Tracking:
        """Update tracking entry"""
        logger.info(f"Updating tracking with id: {tracking.id}")

        obj_data = obj_in.model_dump(exclude_unset=True)

        for field, value in obj_data.items():
            if value is not None:
                setattr(tracking, field, value)

        db.add(tracking)
        await db.commit()

        # Re-query with eager loading
        stmt = (
            select(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(Tracking.id == tracking.id)
        )
        result = await db.execute(stmt)
        tracking = result.unique().scalar_one()

        logger.debug(f"Updated tracking with id: {tracking.id}")
        return tracking

    async def delete(self, db: AsyncSession, *, user_id: int, media_id: int) -> bool:
        """Delete tracking entry"""
        logger.info(f"Deleting tracking for user_id: {user_id}, media_id: {media_id}")

        tracking = await self.get_by_user_and_media(
            db, user_id=user_id, media_id=media_id
        )

        if not tracking:
            logger.warning(
                f"Tracking not found for user_id: {user_id}, media_id: {media_id}"
            )
            return False

        await db.delete(tracking)
        await db.commit()

        logger.debug(f"Deleted tracking with id: {tracking.id}")
        return True

    async def get_statistics(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        media_type: Optional[MediaTypeEnum] = None,
    ) -> dict:
        """Get user's tracking statistics"""
        logger.debug(
            f"Getting statistics for user_id: {user_id} (media_type: {media_type})"
        )

        stmt = select(Tracking).filter(Tracking.user_id == user_id)

        if media_type:
            stmt = stmt.filter(Tracking.media_type == media_type)

        result = await db.execute(stmt)
        all_entries = list(result.scalars().all())

        stats = {
            "total": len(all_entries),
            "completed": len(
                [e for e in all_entries if e.status == TrackingStatusEnum.COMPLETED]
            ),
            "in_progress": len(
                [e for e in all_entries if e.status == TrackingStatusEnum.IN_PROGRESS]
            ),
            "plan_to_watch": len(
                [e for e in all_entries if e.status == TrackingStatusEnum.PLANNED]
            ),
            "dropped": len(
                [e for e in all_entries if e.status == TrackingStatusEnum.DROPPED]
            ),
            "on_hold": len(
                [e for e in all_entries if e.status == TrackingStatusEnum.ON_HOLD]
            ),
            "favorites": len([e for e in all_entries if e.favorite]),
        }

        # Calculate average rating
        rated_entries = [e for e in all_entries if e.rating is not None]
        stats["average_rating"] = (
            sum(e.rating for e in rated_entries) / len(rated_entries)
            if rated_entries
            else 0
        )

        logger.debug(f"Statistics for user_id {user_id}: {stats}")
        return stats


tracking_crud = CRUDTracking(Tracking)
