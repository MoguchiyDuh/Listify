from datetime import date
from typing import List, Optional

from models import MediaTypeEnum
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class MediaBase(BaseModel):
    """Base schema for media"""

    title: str
    description: Optional[str] = None
    release_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    is_custom: bool = False

    @field_validator("cover_image_url")
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate image URL - accept both local paths and external URLs"""
        if v is None:
            return v
        if (
            v.startswith("/static/")
            or v.startswith("http://")
            or v.startswith("https://")
        ):
            return v
        raise ValueError(
            "Image URL must be local path (/static/...) or external URL (http(s)://...)"
        )


class MediaCreate(MediaBase):
    """Schema for creating media"""

    tags: Optional[List[str]] = None


class MediaUpdate(BaseModel):
    """Schema for updating media"""

    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[date] = None
    cover_image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class MediaResponse(MediaBase):
    """Schema for media response"""

    id: int
    media_type: MediaTypeEnum
    tags: Optional[List[str]] = None
    created_by_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def extract_tags(cls, data):
        """Extract tags from tag_associations before validation"""
        if hasattr(data, "tag_associations") and data.tag_associations:
            tags = [
                assoc.tag.name
                for assoc in data.tag_associations
                if hasattr(assoc, "tag") and assoc.tag
            ]
            if isinstance(data, dict):
                data["tags"] = tags
            else:
                # For ORM objects, we need to return a dict
                data_dict = {
                    key: getattr(data, key)
                    for key in dir(data)
                    if not key.startswith("_")
                }
                data_dict["tags"] = tags
                return data_dict
        return data

    model_config = ConfigDict(from_attributes=True)
