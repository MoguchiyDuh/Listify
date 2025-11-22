from typing import Optional

from pydantic import ConfigDict

from models import AgeRatingEnum, MediaStatusEnum

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class AnimeBase(MediaBase):
    """Base schema for anime"""

    original_title: Optional[str] = None
    total_episodes: Optional[int] = None
    studios: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class AnimeCreate(MediaCreate):
    """Schema for creating anime"""

    original_title: Optional[str] = None
    total_episodes: Optional[int] = None
    studios: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class AnimeUpdate(MediaUpdate):
    """Schema for updating anime"""

    original_title: Optional[str] = None
    total_episodes: Optional[int] = None
    studios: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class AnimeResponse(MediaResponse):
    """Schema for anime response"""

    original_title: Optional[str] = None
    total_episodes: Optional[int] = None
    studios: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None

    model_config = ConfigDict(from_attributes=True)
