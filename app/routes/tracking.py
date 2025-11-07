from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import setup_logger
from app.crud import tracking_crud
from app.models import MediaTypeEnum, TrackingStatusEnum, User
from app.routes.deps import get_current_user
from app.schemas.tracking import (TrackingCreate, TrackingResponse,
                                  TrackingUpdate)

logger = setup_logger("api.tracking")

router = APIRouter()


@router.post("/", response_model=TrackingResponse, status_code=status.HTTP_201_CREATED)
def create_tracking(
    tracking: TrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new tracking entry"""
    logger.info(
        f"User {current_user.username} creating tracking for media_id: {tracking.media_id}"
    )

    try:
        return tracking_crud.create(db, obj_in=tracking, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[TrackingResponse])
def get_user_tracking(
    status_filter: Optional[TrackingStatusEnum] = None,
    media_type: Optional[MediaTypeEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all tracking entries for current user"""
    logger.debug(
        f"User {current_user.username} fetching tracking "
        f"(status: {status_filter}, type: {media_type})"
    )

    return tracking_crud.get_by_user(
        db,
        user_id=current_user.id,
        status=status_filter,
        media_type=media_type,
        skip=skip,
        limit=limit,
    )


@router.get("/favorites", response_model=List[TrackingResponse])
def get_favorites(
    media_type: Optional[MediaTypeEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's favorite media"""
    logger.debug(f"User {current_user.username} fetching favorites")

    return tracking_crud.get_favorites(
        db,
        user_id=current_user.id,
        media_type=media_type,
        skip=skip,
        limit=limit,
    )


@router.get("/statistics")
def get_statistics(
    media_type: Optional[MediaTypeEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tracking statistics for current user"""
    logger.debug(f"User {current_user.username} fetching statistics")

    return tracking_crud.get_statistics(
        db, user_id=current_user.id, media_type=media_type
    )


@router.get("/{media_id}", response_model=TrackingResponse)
def get_tracking_by_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tracking entry for specific media"""
    logger.debug(
        f"User {current_user.username} fetching tracking for media_id: {media_id}"
    )

    tracking = tracking_crud.get_by_user_and_media(
        db, user_id=current_user.id, media_id=media_id
    )

    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking entry not found",
        )

    return tracking


@router.put("/{media_id}", response_model=TrackingResponse)
def update_tracking(
    media_id: int,
    tracking_update: TrackingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update tracking entry"""
    logger.info(
        f"User {current_user.username} updating tracking for media_id: {media_id}"
    )

    tracking = tracking_crud.get_by_user_and_media(
        db, user_id=current_user.id, media_id=media_id
    )

    if not tracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking entry not found",
        )

    return tracking_crud.update(db, tracking=tracking, obj_in=tracking_update)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tracking(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete tracking entry"""
    logger.info(
        f"User {current_user.username} deleting tracking for media_id: {media_id}"
    )

    if not tracking_crud.delete(db, user_id=current_user.id, media_id=media_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracking entry not found",
        )
