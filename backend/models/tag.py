from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from core.database import Base

from .media import MediaTypeEnum


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)

    media_associations = relationship(
        "MediaTag", back_populates="tag", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class MediaTag(Base):
    """Association table between Media and Tags"""

    __tablename__ = "media_tags"

    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(
        Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_type = Column(SQLEnum(MediaTypeEnum), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("media_id", "tag_id", name="uq_media_tag"),)

    media = relationship("Media", back_populates="tag_associations")
    tag = relationship("Tag", back_populates="media_associations")

    def __repr__(self):
        return (
            f"<MediaTag(id={self.id}, media_id={self.media_id}, tag_id={self.tag_id})>"
        )
