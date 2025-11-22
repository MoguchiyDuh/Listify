from typing import Optional

from pydantic import ConfigDict

from models import AgeRatingEnum, MediaStatusEnum

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class MangaBase(MediaBase):
    """Base schema for manga"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    authors: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class MangaCreate(MediaCreate):
    """Schema for creating manga"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    authors: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class MangaUpdate(MediaUpdate):
    """Schema for updating manga"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    authors: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class MangaResponse(MediaResponse):
    """Schema for manga response"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    authors: Optional[list] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None

    model_config = ConfigDict(from_attributes=True)
