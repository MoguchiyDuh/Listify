from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import NotFound
from crud import tracking_crud
from models import MediaTypeEnum, TrackingStatusEnum, User
from schemas import TrackingCreate, TrackingResponse, TrackingUpdate

from .base import logger
from .deps import get_current_user

logger = logger.bind(module="tracking")

router = APIRouter()


@router.post("/", response_model=TrackingResponse, status_code=status.HTTP_201_CREATED)
async def create_tracking(
    tracking: TrackingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tracking entry"""
    logger.info(
        f"User {current_user.username} creating tracking for media_id: {tracking.media_id}"
    )

    return await tracking_crud.create(db, obj_in=tracking, user_id=current_user.id)


@router.get("/", response_model=List[TrackingResponse])
async def get_user_tracking(
    status: Optional[TrackingStatusEnum] = None,
    media_type: Optional[MediaTypeEnum] = None,
    sort_by: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tracking entries for current user"""
    logger.debug(
        f"User {current_user.username} fetching tracking "
        f"(status: {status}, type: {media_type}, sort_by: {sort_by})"
    )

    return await tracking_crud.get_by_user(
        db,
        user_id=current_user.id,
        status=status,
        media_type=media_type,
        sort_by=sort_by,
        skip=skip,
        limit=limit,
    )


@router.get("/favorites", response_model=List[TrackingResponse])
async def get_favorites(
    media_type: Optional[MediaTypeEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's favorite media"""
    logger.debug(f"User {current_user.username} fetching favorites")

    return await tracking_crud.get_favorites(
        db,
        user_id=current_user.id,
        media_type=media_type,
        skip=skip,
        limit=limit,
    )


@router.get("/statistics")
async def get_statistics(
    media_type: Optional[MediaTypeEnum] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tracking statistics for current user"""
    logger.debug(f"User {current_user.username} fetching statistics")

    return await tracking_crud.get_statistics(
        db, user_id=current_user.id, media_type=media_type
    )


@router.get("/{media_id}", response_model=TrackingResponse)
async def get_tracking_by_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tracking entry for specific media"""
    logger.debug(
        f"User {current_user.username} fetching tracking for media_id: {media_id}"
    )

    tracking = await tracking_crud.get_by_user_and_media(
        db, user_id=current_user.id, media_id=media_id
    )

    if not tracking:
        raise NotFound("Tracking entry", str(media_id))

    return tracking


@router.put("/{media_id}", response_model=TrackingResponse)
@router.patch("/{media_id}", response_model=TrackingResponse)
async def update_tracking(
    media_id: int,
    tracking_update: TrackingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update tracking entry"""
    logger.info(
        f"User {current_user.username} updating tracking for media_id: {media_id}"
    )

    tracking = await tracking_crud.get_by_user_and_media(
        db, user_id=current_user.id, media_id=media_id
    )

    if not tracking:
        raise NotFound("Tracking entry", str(media_id))

    return await tracking_crud.update(db, tracking=tracking, obj_in=tracking_update)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tracking(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete tracking entry"""
    logger.info(
        f"User {current_user.username} deleting tracking for media_id: {media_id}"
    )

    if not await tracking_crud.delete(db, user_id=current_user.id, media_id=media_id):
        raise NotFound("Tracking entry", str(media_id))
