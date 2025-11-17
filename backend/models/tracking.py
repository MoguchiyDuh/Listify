from enum import Enum

from core.database import Base
from sqlalchemy import Boolean, Column, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .media import MediaTypeEnum


class TrackingStatusEnum(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"
    ON_HOLD = "on_hold"


class Tracking(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_id = Column(
        Integer, ForeignKey("media.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_type = Column(SQLEnum(MediaTypeEnum), nullable=False, index=True)

    # Tracking fields
    status = Column(SQLEnum(TrackingStatusEnum), nullable=False)
    rating = Column(Float, nullable=True)  # 0-10 scale
    progress = Column(Integer, default=0)  # episodes watched, chapters read, etc.

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    favorite = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    # Unique constraint: one tracking entry per user per media
    __table_args__ = (UniqueConstraint("user_id", "media_id", name="uq_user_media"),)

    # Relationships
    user = relationship("User", back_populates="tracking_entries")
    media = relationship("Media", back_populates="tracking_entries")

    def __repr__(self):
        return f"<Tracking(id={self.id}, user_id={self.user_id}, media_id={self.media_id}, status={self.status})>"
