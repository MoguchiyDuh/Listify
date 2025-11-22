from typing import List, Optional

from pydantic import ConfigDict

from models import PlatformEnum

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class GameBase(MediaBase):
    """Base schema for games"""

    platforms: Optional[List[PlatformEnum]] = None
    developers: Optional[list] = None
    publishers: Optional[list] = None


class GameCreate(MediaCreate):
    """Schema for creating a game"""

    platforms: Optional[List[PlatformEnum]] = None
    developers: Optional[list] = None
    publishers: Optional[list] = None


class GameUpdate(MediaUpdate):
    """Schema for updating a game"""

    platforms: Optional[List[PlatformEnum]] = None
    developers: Optional[list] = None
    publishers: Optional[list] = None


class GameResponse(MediaResponse):
    """Schema for game response"""

    platforms: Optional[List[PlatformEnum]] = None
    developers: Optional[list] = None
    publishers: Optional[list] = None

    model_config = ConfigDict(from_attributes=True)
