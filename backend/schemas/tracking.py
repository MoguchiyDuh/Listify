from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from models import MediaTypeEnum, TrackingStatusEnum
from schemas import (
    AnimeResponse,
    BookResponse,
    GameResponse,
    MangaResponse,
    MovieResponse,
    SeriesResponse,
)


class TrackingBase(BaseModel):
    """Base schema for tracking"""

    status: TrackingStatusEnum
    rating: Optional[float] = Field(None, ge=0, le=10)
    progress: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    favorite: bool = False
    notes: Optional[str] = None


class TrackingCreate(TrackingBase):
    """Schema for creating tracking entry"""

    media_id: int
    media_type: MediaTypeEnum


class TrackingUpdate(BaseModel):
    """Schema for updating tracking entry"""

    status: Optional[TrackingStatusEnum] = None
    rating: Optional[float] = Field(None, ge=0, le=10)
    progress: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    favorite: Optional[bool] = None
    notes: Optional[str] = None


class TrackingResponse(TrackingBase):
    """Schema for tracking response"""

    id: int
    user_id: int
    media_id: int
    media_type: MediaTypeEnum
    media: Optional[
        Union[
            MovieResponse,
            SeriesResponse,
            AnimeResponse,
            MangaResponse,
            BookResponse,
            GameResponse,
        ]
    ] = None

    model_config = ConfigDict(from_attributes=True)
