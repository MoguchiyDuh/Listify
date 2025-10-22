from datetime import date, datetime
from typing import List, Optional

from app.models import MediaTypeEnum
from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    runtime: Optional[int] = Field(None, gt=0)
    director: Optional[str] = Field(None, max_length=255)
    is_custom: bool = False


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    runtime: Optional[int] = Field(None, gt=0)
    director: Optional[str] = Field(None, max_length=255)


class MovieResponse(MovieBase):
    id: int
    media_type: MediaTypeEnum
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
