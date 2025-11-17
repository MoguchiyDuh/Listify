from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class TagResponse(TagBase):
    id: int
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MediaTagCreate(BaseModel):
    media_id: int
    tag_id: int


class MediaTagResponse(BaseModel):
    id: int
    media_id: int
    tag_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
