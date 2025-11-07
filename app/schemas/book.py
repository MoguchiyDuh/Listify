from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.media import MediaBase, MediaResponse, MediaUpdate


class BookBase(MediaBase):
    """Base schema for books"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None


class BookCreate(BookBase):
    """Schema for creating a book"""

    pass


class BookUpdate(MediaUpdate):
    """Schema for updating a book"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None


class BookResponse(BookBase):
    """Schema for book response"""

    id: int

    model_config = ConfigDict(from_attributes=True)
