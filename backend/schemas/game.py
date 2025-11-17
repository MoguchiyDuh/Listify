from typing import List, Optional

from models import PlatformEnum
from pydantic import ConfigDict

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class GameBase(MediaBase):
    """Base schema for games"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameCreate(MediaCreate):
    """Schema for creating a game"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameUpdate(MediaUpdate):
    """Schema for updating a game"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameResponse(MediaResponse):
    """Schema for game response"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
