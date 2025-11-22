from typing import Optional

from pydantic import ConfigDict

from models import MediaStatusEnum

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class SeriesBase(MediaBase):
    """Base schema for TV series"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None
    directors: Optional[list] = None


class SeriesCreate(MediaCreate):
    """Schema for creating a series"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None
    directors: Optional[list] = None


class SeriesUpdate(MediaUpdate):
    """Schema for updating a series"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None
    directors: Optional[list] = None


class SeriesResponse(MediaResponse):
    """Schema for series response"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None
    directors: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)
