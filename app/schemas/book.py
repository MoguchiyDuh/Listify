from datetime import date, datetime
from typing import List, Optional

from app.models import MediaTypeEnum
from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    pages: Optional[int] = Field(None, gt=0)
    author: Optional[str] = Field(None, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20, pattern=r"^[\d-]+$")
    is_custom: bool = False


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_date: Optional[date] = None
    image: Optional[str] = Field(None, max_length=500)
    pages: Optional[int] = Field(None, gt=0)
    author: Optional[str] = Field(None, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20, pattern=r"^[\d-]+$")


class BookResponse(BookBase):
    id: int
    media_type: MediaTypeEnum
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)
