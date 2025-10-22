from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import MediaTypeEnum
from app.models.game import PlatformEnum


class GameBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    platform: PlatformEnum = PlatformEnum.PC
    developer: Optional[str] = Field(None, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    steam_id: Optional[str] = Field(None, max_length=255)
    is_custom: bool = False


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    platform: Optional[PlatformEnum] = None
    developer: Optional[str] = Field(None, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    steam_id: Optional[str] = Field(None, max_length=255)


class GameResponse(GameBase):
    id: int
    media_type: MediaTypeEnum
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
