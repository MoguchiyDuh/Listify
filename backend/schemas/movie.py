from typing import Optional

from pydantic import ConfigDict

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class MovieBase(MediaBase):
    """Base schema for movies"""

    runtime: Optional[int] = None


class MovieCreate(MediaCreate):
    """Schema for creating a movie"""

    runtime: Optional[int] = None


class MovieUpdate(MediaUpdate):
    """Schema for updating a movie"""

    runtime: Optional[int] = None


class MovieResponse(MediaResponse):
    """Schema for movie response"""

    runtime: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
