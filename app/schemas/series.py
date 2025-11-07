from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import MediaStatusEnum
from app.schemas.media import MediaBase, MediaResponse, MediaUpdate


class SeriesBase(MediaBase):
    """Base schema for TV series"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None


class SeriesCreate(SeriesBase):
    """Schema for creating a series"""

    pass


class SeriesUpdate(MediaUpdate):
    """Schema for updating a series"""

    total_episodes: Optional[int] = None
    seasons: Optional[int] = None
    status: Optional[MediaStatusEnum] = None


class SeriesResponse(SeriesBase):
    """Schema for series response"""

    id: int

    model_config = ConfigDict(from_attributes=True)
