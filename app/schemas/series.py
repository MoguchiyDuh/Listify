from datetime import date, datetime
from typing import List, Optional

from app.models import MediaTypeEnum
from app.models.media import AnimeSeriesStatusEnum
from pydantic import BaseModel, ConfigDict, Field


class SeriesBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    total_episodes: Optional[int] = Field(None, gt=0)
    seasons: Optional[int] = Field(None, gt=0)
    status: Optional[AnimeSeriesStatusEnum] = AnimeSeriesStatusEnum.FINISHED
    is_custom: bool = False


class SeriesCreate(SeriesBase):
    pass


class SeriesUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    total_episodes: Optional[int] = Field(None, gt=0)
    seasons: Optional[int] = Field(None, gt=0)
    status: Optional[AnimeSeriesStatusEnum] = None


class SeriesResponse(SeriesBase):
    id: int
    media_type: MediaTypeEnum
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
