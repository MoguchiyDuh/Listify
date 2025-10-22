from datetime import date, datetime
from typing import List, Optional

from app.models import MediaTypeEnum
from pydantic import BaseModel, ConfigDict, Field


class MediaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    is_custom: bool = False


class MediaCreate(MediaBase):
    media_type: MediaTypeEnum


class MediaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)


class MediaResponse(MediaBase):
    id: int
    media_type: MediaTypeEnum
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
