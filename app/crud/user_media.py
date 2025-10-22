from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.core import setup_logger
from app.models import MediaTypeEnum, PriorityEnum, StatusEnum, UserMedia
from app.schemas import UserMediaCreate, UserMediaUpdate
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

logger = setup_logger(__name__)


class UserMediaCRUD:
    @staticmethod
    def create(
        db: Session, user_id: UUID, user_media_data: UserMediaCreate
    ) -> UserMedia:
        logger.debug(
            f"Creating user media entry - user: {user_id}, media: {user_media_data.media_id}"
        )

        user_media = UserMedia(user_id=user_id, **user_media_data.model_dump())

        if user_media.status == StatusEnum.COMPLETED:
            user_media.complete_date = datetime.now(timezone.utc)

        db.add(user_media)
        db.commit()
        db.refresh(user_media)

        logger.debug(f"User media entry created successfully: {user_media.id}")
        return user_media

    @staticmethod
    def get_by_id(
        db: Session, user_media_id: int, user_id: UUID
    ) -> Optional[UserMedia]:
        logger.debug(f"Fetching user media by ID: {user_media_id}, user: {user_id}")

        user_media = (
            db.query(UserMedia)
            .filter(and_(UserMedia.id == user_media_id, UserMedia.user_id == user_id))
            .first()
        )

        if user_media:
            logger.debug(f"User media found: {user_media.id}")
        else:
            logger.debug(f"User media not found: {user_media_id}")

        return user_media

    @staticmethod
    def get_by_media_id(
        db: Session, media_id: int, user_id: UUID
    ) -> Optional[UserMedia]:
        logger.debug(f"Fetching user media by media ID: {media_id}, user: {user_id}")

        user_media = (
            db.query(UserMedia)
            .filter(and_(UserMedia.media_id == media_id, UserMedia.user_id == user_id))
            .first()
        )

        if user_media:
            logger.debug(f"User media found: {user_media.id}")
        else:
            logger.debug(f"User media not found for media: {media_id}")

        return user_media

    @staticmethod
    def get_user_list(
        db: Session,
        user_id: UUID,
        status: Optional[StatusEnum] = None,
        priority: Optional[PriorityEnum] = None,
        media_type: Optional[MediaTypeEnum] = None,
        is_favorite: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserMedia]:
        logger.debug(
            f"Fetching user media list - user: {user_id}, status: {status}, "
            f"priority: {priority}, type: {media_type}, favorite: {is_favorite}"
        )

        query = (
            db.query(UserMedia)
            .options(joinedload(UserMedia.media))
            .filter(UserMedia.user_id == user_id)
        )

        if status:
            query = query.filter(UserMedia.status == status)

        if priority:
            query = query.filter(UserMedia.priority == priority)

        if is_favorite is not None:
            query = query.filter(UserMedia.is_favorite == is_favorite)

        if media_type:
            query = query.join(UserMedia.media).filter(
                UserMedia.media.has(media_type=media_type)
            )

        user_media_list = query.offset(skip).limit(limit).all()

        logger.debug(f"Found {len(user_media_list)} user media entries")
        return user_media_list

    @staticmethod
    def update(
        db: Session, user_media_id: int, user_id: UUID, user_media_data: UserMediaUpdate
    ) -> Optional[UserMedia]:
        logger.debug(f"Updating user media: {user_media_id}, user: {user_id}")

        user_media = (
            db.query(UserMedia)
            .filter(and_(UserMedia.id == user_media_id, UserMedia.user_id == user_id))
            .first()
        )

        if not user_media:
            logger.debug(f"User media not found for update: {user_media_id}")
            return None

        update_data = user_media_data.model_dump(exclude_unset=True)

        # Handle status change to completed
        if "status" in update_data:
            if (
                update_data["status"] == StatusEnum.COMPLETED
                and user_media.status != StatusEnum.COMPLETED
            ):
                update_data["complete_date"] = datetime.now(timezone.utc)
            elif update_data["status"] != StatusEnum.COMPLETED:
                update_data["complete_date"] = None

        for field, value in update_data.items():
            setattr(user_media, field, value)

        db.commit()
        db.refresh(user_media)

        logger.debug(f"User media updated successfully: {user_media.id}")
        return user_media

    @staticmethod
    def delete(db: Session, user_media_id: int, user_id: UUID) -> bool:
        logger.debug(f"Deleting user media: {user_media_id}, user: {user_id}")

        user_media = (
            db.query(UserMedia)
            .filter(and_(UserMedia.id == user_media_id, UserMedia.user_id == user_id))
            .first()
        )

        if not user_media:
            logger.debug(f"User media not found for deletion: {user_media_id}")
            return False

        db.delete(user_media)
        db.commit()

        logger.debug(f"User media deleted successfully: {user_media_id}")
        return True

    @staticmethod
    def exists(db: Session, user_id: UUID, media_id: int) -> bool:
        logger.debug(
            f"Checking user media existence - user: {user_id}, media: {media_id}"
        )

        exists = (
            db.query(UserMedia)
            .filter(and_(UserMedia.user_id == user_id, UserMedia.media_id == media_id))
            .first()
            is not None
        )

        logger.debug(f"User media exists: {exists}")
        return exists

    @staticmethod
    def get_statistics(db: Session, user_id: UUID) -> dict:
        logger.debug(f"Calculating statistics for user: {user_id}")

        stats = {
            "total": db.query(func.count(UserMedia.id))
            .filter(UserMedia.user_id == user_id)
            .scalar(),
            "completed": db.query(func.count(UserMedia.id))
            .filter(
                and_(
                    UserMedia.user_id == user_id,
                    UserMedia.status == StatusEnum.COMPLETED,
                )
            )
            .scalar(),
            "in_progress": db.query(func.count(UserMedia.id))
            .filter(
                and_(
                    UserMedia.user_id == user_id,
                    UserMedia.status == StatusEnum.IN_PROGRESS,
                )
            )
            .scalar(),
            "planning": db.query(func.count(UserMedia.id))
            .filter(
                and_(
                    UserMedia.user_id == user_id,
                    UserMedia.status == StatusEnum.PLANNING,
                )
            )
            .scalar(),
            "dropped": db.query(func.count(UserMedia.id))
            .filter(
                and_(
                    UserMedia.user_id == user_id, UserMedia.status == StatusEnum.DROPPED
                )
            )
            .scalar(),
            "on_hold": db.query(func.count(UserMedia.id))
            .filter(
                and_(
                    UserMedia.user_id == user_id, UserMedia.status == StatusEnum.ON_HOLD
                )
            )
            .scalar(),
            "favorites": db.query(func.count(UserMedia.id))
            .filter(and_(UserMedia.user_id == user_id, UserMedia.is_favorite == True))
            .scalar(),
        }

        logger.debug(f"Statistics calculated: {stats}")
        return stats

    @staticmethod
    def get_by_priority_sorted(
        db: Session, user_id: UUID, status: Optional[StatusEnum] = None, limit: int = 50
    ) -> List[UserMedia]:
        logger.debug(
            f"Fetching user media sorted by priority - user: {user_id}, status: {status}"
        )

        priority_order = {
            PriorityEnum.HIGH: 1,
            PriorityEnum.MEDIUM: 2,
            PriorityEnum.LOW: 3,
            PriorityEnum.NONE: 4,
        }

        query = (
            db.query(UserMedia)
            .options(joinedload(UserMedia.media))
            .filter(UserMedia.user_id == user_id)
        )

        if status:
            query = query.filter(UserMedia.status == status)

        user_media_list = query.all()

        # Sort by priority
        sorted_list = sorted(
            user_media_list, key=lambda x: priority_order.get(x.priority, 999)
        )[:limit]

        logger.debug(f"Found {len(sorted_list)} sorted user media entries")
        return sorted_list
