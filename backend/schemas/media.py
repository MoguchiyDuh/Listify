from datetime import date
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from core.logger import setup_logger
from models import MediaTypeEnum

logger = setup_logger("schemas")


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
    def extract_tags(cls, data: Any) -> Any:
        """Extract tags from tag_associations before validation"""
        if hasattr(data, "tag_associations"):
            # Simple check if we can safely access tag_associations
            try:
                if data.tag_associations is not None:
                    tags = []
                    for assoc in data.tag_associations:
                        if (
                            hasattr(assoc, "tag")
                            and assoc.tag
                            and hasattr(assoc.tag, "name")
                        ):
                            tags.append(assoc.tag.name)
                    # Convert to dict for Pydantic
                    if hasattr(data, "__dict__"):
                        data_dict = data.__dict__.copy()
                        data_dict["tags"] = tags
                        return data_dict
            except (AttributeError, RuntimeError) as e:
                # If there's any issue accessing relationships, skip tag extraction
                logger.warning(f"Warning: Could not extract tags: {e}")

        elif isinstance(data, dict) and "tag_associations" in data:
            # Handle dict input
            tag_associations = data.get("tag_associations")
            if tag_associations:
                tags = []
                for assoc in tag_associations:
                    if (
                        hasattr(assoc, "tag")
                        and assoc.tag
                        and hasattr(assoc.tag, "name")
                    ):
                        tags.append(assoc.tag.name)
                data["tags"] = tags

        return data

    model_config = ConfigDict(from_attributes=True)
