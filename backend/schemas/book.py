from typing import Optional

from pydantic import ConfigDict

from .media import MediaBase, MediaCreate, MediaResponse, MediaUpdate


class BookBase(MediaBase):
    """Base schema for books"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None


class BookCreate(MediaCreate):
    """Schema for creating a book"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None


class BookUpdate(MediaUpdate):
    """Schema for updating a book"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None


class BookResponse(MediaResponse):
    """Schema for book response"""

    pages: Optional[int] = None
    author: Optional[str] = None
    isbn: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
