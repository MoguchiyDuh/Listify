from typing import Optional

from pydantic import ConfigDict

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class MovieBase(MediaBase):
    """Base schema for movies"""

    directors: Optional[list] = None
    runtime: Optional[int] = None


class MovieCreate(MediaCreate):
    """Schema for creating a movie"""

    directors: Optional[list] = None
    runtime: Optional[int] = None


class MovieUpdate(MediaUpdate):
    """Schema for updating a movie"""

    directors: Optional[list] = None
    runtime: Optional[int] = None


class MovieResponse(MediaResponse):
    """Schema for movie response"""

    directors: Optional[list] = None
    runtime: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
