from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.database import Base

from .media import MediaTypeEnum


class TrackingStatusEnum(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DROPPED = "dropped"
    ON_HOLD = "on_hold"


class TrackingPriorityEnum(str, Enum):
    LOW = "low"
    MID = "mid"
    HIGH = "high"


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

    status = Column(SQLEnum(TrackingStatusEnum), nullable=False)
    priority = Column(SQLEnum(TrackingPriorityEnum), nullable=True)
    rating = Column(Float, nullable=True)
    progress = Column(Integer, default=0)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    favorite = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "media_id", name="uq_user_media"),
        CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_range"),
    )

    user = relationship("User", back_populates="tracking_entries")
    media = relationship("Media", back_populates="tracking_entries")

    def __repr__(self):
        return f"<Tracking(id={self.id}, user_id={self.user_id}, media_id={self.media_id}, status={self.status})>"
