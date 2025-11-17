from typing import List, Optional

from models import Media, MediaTag, MediaTypeEnum, Tracking, TrackingStatusEnum
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from .base import CRUDBase, logger

logger = logger.getChild("tracking")


class CRUDTracking(CRUDBase[Tracking]):
    """CRUD operations for tracking"""

    def get_by_user_and_media(
        self, db: Session, *, user_id: int, media_id: int
    ) -> Optional[Tracking]:
        """Get tracking entry for user and media"""
        logger.debug(f"Getting tracking for user_id: {user_id}, media_id: {media_id}")
        return (
            db.query(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(and_(Tracking.user_id == user_id, Tracking.media_id == media_id))
            .first()
        )

    def get_by_user(
        self,
        db: Session,
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

        query = (
            db.query(Tracking)
            .options(
                joinedload(Tracking.media)
                .joinedload(Media.tag_associations)
                .joinedload(MediaTag.tag)
            )
            .filter(Tracking.user_id == user_id)
        )

        if status:
            query = query.filter(Tracking.status == status)

        if media_type:
            query = query.filter(Tracking.media_type == media_type)

        return query.offset(skip).limit(limit).all()

    def get_favorites(
        self,
        db: Session,
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

        query = (
            db.query(Tracking)
            .options(joinedload(Tracking.media))
            .filter(and_(Tracking.user_id == user_id, Tracking.favorite.is_(True)))
        )

        if media_type:
            query = query.filter(Tracking.media_type == media_type)

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: BaseModel, user_id: int) -> Tracking:
        """Create tracking entry"""
        logger.info(f"Creating tracking for user_id: {user_id}")

        obj_data = obj_in.model_dump(exclude_unset=True)
        obj_data["user_id"] = user_id

        # Check if tracking already exists
        existing = self.get_by_user_and_media(
            db, user_id=user_id, media_id=obj_data["media_id"]
        )

        if existing:
            logger.warning(
                f"Tracking already exists for user_id: {user_id}, "
                f"media_id: {obj_data['media_id']}"
            )
            raise ValueError("Tracking entry already exists for this media")

        tracking = Tracking(**obj_data)
        db.add(tracking)
        db.commit()
        db.refresh(tracking)

        logger.debug(f"Created tracking with id: {tracking.id}")
        return tracking

    def update(self, db: Session, *, tracking: Tracking, obj_in: BaseModel) -> Tracking:
        """Update tracking entry"""
        logger.info(f"Updating tracking with id: {tracking.id}")

        obj_data = obj_in.model_dump(exclude_unset=True)

        for field, value in obj_data.items():
            if value is not None:
                setattr(tracking, field, value)

        db.add(tracking)
        db.commit()
        db.refresh(tracking)

        logger.debug(f"Updated tracking with id: {tracking.id}")
        return tracking

    def delete(self, db: Session, *, user_id: int, media_id: int) -> bool:
        """Delete tracking entry"""
        logger.info(f"Deleting tracking for user_id: {user_id}, media_id: {media_id}")

        tracking = self.get_by_user_and_media(db, user_id=user_id, media_id=media_id)

        if not tracking:
            logger.warning(
                f"Tracking not found for user_id: {user_id}, media_id: {media_id}"
            )
            return False

        db.delete(tracking)
        db.commit()

        logger.debug(f"Deleted tracking with id: {tracking.id}")
        return True

    def get_statistics(
        self, db: Session, *, user_id: int, media_type: Optional[MediaTypeEnum] = None
    ) -> dict:
        """Get user's tracking statistics"""
        logger.debug(
            f"Getting statistics for user_id: {user_id} (media_type: {media_type})"
        )

        query = db.query(Tracking).filter(Tracking.user_id == user_id)

        if media_type:
            query = query.filter(Tracking.media_type == media_type)

        all_entries = query.all()

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
