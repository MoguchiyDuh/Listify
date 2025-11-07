from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import AgeRatingEnum, MediaStatusEnum
from app.schemas.media import MediaBase, MediaResponse, MediaUpdate


class MangaBase(MediaBase):
    """Base schema for manga"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    author: Optional[str] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class MangaCreate(MangaBase):
    """Schema for creating manga"""

    pass


class MangaUpdate(MediaUpdate):
    """Schema for updating manga"""

    original_title: Optional[str] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    author: Optional[str] = None
    status: Optional[MediaStatusEnum] = None
    age_rating: Optional[AgeRatingEnum] = None


class MangaResponse(MangaBase):
    """Schema for manga response"""

    id: int

    model_config = ConfigDict(from_attributes=True)
