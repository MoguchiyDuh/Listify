from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models import PriorityEnum, StatusEnum
from pydantic import BaseModel, ConfigDict, Field


class UserMediaBase(BaseModel):
    status: StatusEnum = StatusEnum.PLANNING
    priority: PriorityEnum = PriorityEnum.MEDIUM
    rating: Optional[int] = Field(None, ge=1, le=10)
    progress: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    is_favorite: bool = False


class UserMediaCreate(UserMediaBase):
    media_id: int


class UserMediaUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    priority: Optional[PriorityEnum] = None
    rating: Optional[int] = Field(None, ge=1, le=10)
    progress: Optional[int] = Field(None, ge=0)
    note: Optional[str] = None
    is_favorite: Optional[bool] = None


class UserMediaResponse(UserMediaBase):
    id: int
    user_id: UUID
    media_id: int
    complete_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserMediaWithMedia(UserMediaResponse):
    media: dict
