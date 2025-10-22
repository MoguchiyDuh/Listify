from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from .media import MediaTypeEnum


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    slug = Column(String(50), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    media_associations = relationship(
        "MediaTag", back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class MediaTag(Base):
    __tablename__ = "media_tags"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(
        Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_type = Column(Enum(MediaTypeEnum), nullable=False, index=True)
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    # Relationships
    tag = relationship("Tag", back_populates="media_associations")

    # Constraints
    __table_args__ = (UniqueConstraint("media_id", "tag_id", name="unique_media_tag"),)

    def __repr__(self):
        return f"<MediaTag(media_id={self.media_id}, tag_id={self.tag_id})>"
