from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import and_, case, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from core.exceptions import AlreadyExists
from models import (
    Media,
    MediaTag,
    MediaTypeEnum,
    Tracking,
    TrackingPriorityEnum,
    TrackingStatusEnum,
)

from .base import CRUDBase, logger
from .media import media_crud

logger = logger.bind(module="tracking")


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
        sort_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tracking]:
        """Get all tracking entries for a user, optionally filtered"""
        logger.debug(
            f"Getting tracking for user_id: {user_id} "
            f"(status: {status}, media_type: {media_type}, sort_by: {sort_by}, skip: {skip}, limit: {limit})"
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

        # Apply sorting
        if sort_by == "priority":
            # Map priority Enum to numeric values for sorting
            priority_order = case(
                (Tracking.priority == TrackingPriorityEnum.HIGH, 3),
                (Tracking.priority == TrackingPriorityEnum.MID, 2),
                (Tracking.priority == TrackingPriorityEnum.LOW, 1),
                else_=0,
            )
            stmt = stmt.order_by(desc(priority_order), Tracking.id.desc())
        elif sort_by == "rating":
            stmt = stmt.order_by(desc(Tracking.rating), Tracking.id.desc())
        elif sort_by == "title":
            stmt = stmt.join(Tracking.media).order_by(Media.title.asc(), Tracking.id.desc())
        elif sort_by == "created_at":
            # Using ID as proxy for creation date
            stmt = stmt.order_by(Tracking.id.desc())
        else:
            # Default sort for Planned is Priority, otherwise ID
            if status == TrackingStatusEnum.PLANNED:
                priority_order = case(
                    (Tracking.priority == TrackingPriorityEnum.HIGH, 3),
                    (Tracking.priority == TrackingPriorityEnum.MID, 2),
                    (Tracking.priority == TrackingPriorityEnum.LOW, 1),
                    else_=0,
                )
                stmt = stmt.order_by(desc(priority_order), Tracking.id.desc())
            else:
                stmt = stmt.order_by(Tracking.id.desc())

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

    async def _apply_data_integrity_rules(self, db_obj: Tracking) -> None:
        """
        Apply status-based data integrity rules:
        - Planned: Nullify rating, progress, dates.
        - In Progress: Set start_date if null.
        - Completed/Dropped: Set end_date if null.
        - Priority: Only for Planned.
        """
        # Rule: Priority is ONLY for Planned
        if db_obj.status != TrackingStatusEnum.PLANNED:
            db_obj.priority = None

        # Rule: Planned has no rating, progress, or dates
        if db_obj.status == TrackingStatusEnum.PLANNED:
            db_obj.rating = None
            db_obj.progress = 0
            db_obj.start_date = None
            db_obj.end_date = None

        # Rule: Auto-set start_date for in_progress
        if db_obj.status == TrackingStatusEnum.IN_PROGRESS and db_obj.start_date is None:
            db_obj.start_date = date.today()

        # Rule: Auto-set end_date for completed/dropped
        if db_obj.status in [TrackingStatusEnum.COMPLETED, TrackingStatusEnum.DROPPED]:
            if db_obj.end_date is None:
                db_obj.end_date = date.today()

        # Rule: Moving AWAY from completed/dropped nullifies end_date
        if db_obj.status not in [
            TrackingStatusEnum.COMPLETED,
            TrackingStatusEnum.DROPPED,
        ]:
            db_obj.end_date = None

    async def create(
        self, db: AsyncSession, *, obj_in: BaseModel, user_id: int
    ) -> Tracking:
        """Create tracking entry"""
        logger.info(f"Creating tracking for user_id: {user_id}")

        obj_data = obj_in.model_dump(exclude_unset=True)
        obj_data["user_id"] = user_id

        existing = await self.get_by_user_and_media(
            db, user_id=user_id, media_id=obj_data["media_id"]
        )

        if existing:
            logger.warning(
                f"Tracking already exists for user_id: {user_id}, "
                f"media_id: {obj_data['media_id']}"
            )
            raise AlreadyExists("Tracking entry", str(obj_data["media_id"]))

        tracking = Tracking(**obj_data)

        # Apply data integrity rules before saving
        await self._apply_data_integrity_rules(tracking)

        db.add(tracking)
        await db.commit()

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
            setattr(tracking, field, value)

        # Apply data integrity rules after applying updates
        await self._apply_data_integrity_rules(tracking)

        db.add(tracking)
        await db.commit()

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

        # Check if media is custom and record it for cleanup
        is_custom = tracking.media.is_custom
        media_owner_id = tracking.media.created_by_id

        await db.delete(tracking)

        if is_custom:
            logger.info(f"Media {media_id} is custom, deleting it as well")
            await media_crud.delete(
                db, id=media_id, user_id=media_owner_id, commit=False
            )

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

        rated_entries = [e for e in all_entries if e.rating is not None]
        stats["average_rating"] = (
            sum(e.rating for e in rated_entries) / len(rated_entries)
            if rated_entries
            else 0
        )

        if not media_type:
            by_type = {}
            for m_type in MediaTypeEnum:
                by_type[m_type.value] = len(
                    [e for e in all_entries if e.media_type == m_type]
                )
            stats["by_type"] = by_type

        logger.debug(f"Statistics for user_id {user_id}: {stats}")
        return stats


tracking_crud = CRUDTracking(Tracking)
