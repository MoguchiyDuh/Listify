from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models import MediaTypeEnum


class MediaBase(BaseModel):
    """Base schema for media"""

    title: str
    description: Optional[str] = None
    release_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    is_custom: bool = False
    tags: Optional[List[str]] = None


class MediaCreate(MediaBase):
    """Schema for creating media"""

    pass


class MediaUpdate(BaseModel):
    """Schema for updating media"""

    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class MediaResponse(MediaBase):
    """Schema for media response"""

    id: int
    media_type: MediaTypeEnum

    model_config = ConfigDict(from_attributes=True)
