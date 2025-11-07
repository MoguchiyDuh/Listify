from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models import PlatformEnum
from app.schemas.media import MediaBase, MediaResponse, MediaUpdate


class GameBase(MediaBase):
    """Base schema for games"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameCreate(GameBase):
    """Schema for creating a game"""

    pass


class GameUpdate(MediaUpdate):
    """Schema for updating a game"""

    platforms: Optional[List[PlatformEnum]] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None


class GameResponse(GameBase):
    """Schema for game response"""

    id: int

    model_config = ConfigDict(from_attributes=True)
