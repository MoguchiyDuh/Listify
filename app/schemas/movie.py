from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.media import MediaBase, MediaResponse, MediaUpdate


class MovieBase(MediaBase):
    """Base schema for movies"""

    runtime: Optional[int] = None


class MovieCreate(MovieBase):
    """Schema for creating a movie"""

    pass


class MovieUpdate(MediaUpdate):
    """Schema for updating a movie"""

    runtime: Optional[int] = None


class MovieResponse(MovieBase):
    """Schema for movie response"""

    id: int

    model_config = ConfigDict(from_attributes=True)
