import enum
from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship


class MediaTypeEnum(str, enum.Enum):
    MOVIE = "movie"
    SERIES = "series"
    ANIME = "anime"
    BOOK = "book"
    GAME = "game"


class StatusEnum(str, enum.Enum):
    PLANNING = "planning"
    ON_HOLD = "on_hold"
    DROPPED = "dropped"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"


class PriorityEnum(str, enum.Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnimeSeriesStatusEnum(str, enum.Enum):
    AIRING = "airing"
    FINISHED = "finished"
    UPCOMING = "upcoming"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    media_type = Column(Enum(MediaTypeEnum), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    image = Column(String(500), nullable=True)
    is_custom = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False,
    )

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "media",
        "polymorphic_on": media_type,
    }

    # Relationships
    user_media = relationship(
        "UserMedia", back_populates="media", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Media(id={self.id}, title={self.title}, type={self.media_type})>"
