from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import (Boolean, CheckConstraint, Column, DateTime, Enum,
                        ForeignKey, Integer, String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .media import PriorityEnum, StatusEnum


class UserMedia(Base):
    __tablename__ = "user_media"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    media_id = Column(
        Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.PLANNING)
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.MEDIUM)
    rating = Column(Integer, nullable=True)
    progress = Column(Integer, nullable=True)
    note = Column(String, nullable=True)
    complete_date = Column(DateTime, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="user_media")
    media = relationship("Media", back_populates="user_media")

    # Constraints
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="rating_range"),
    )

    def __repr__(self):
        return f"<UserMedia(id={self.id}, user_id={self.user_id}, media_id={self.media_id}, status={self.status})>"
