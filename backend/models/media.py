from enum import Enum

from sqlalchemy import Boolean, Column, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class MediaTypeEnum(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    ANIME = "anime"
    MANGA = "manga"
    BOOK = "book"
    GAME = "game"


class MediaStatusEnum(str, Enum):
    AIRING = "airing"
    FINISHED = "finished"
    UPCOMING = "upcoming"
    CANCELLED = "cancelled"


class AgeRatingEnum(str, Enum):
    G = "G"  # General Audiences
    PG = "PG"  # Parental Guidance
    PG_13 = "PG-13"  # Parents Strongly Cautioned
    R = "R"  # Restricted
    R_PLUS = "R+"  # Mild Nudity
    RX = "Rx"  # Hentai
    NC_17 = "NC-17"  # Adults Only
    UNKNOWN = "Unknown"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    media_type = Column(SQLEnum(MediaTypeEnum), nullable=False, index=True)

    # Common fields
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    release_date = Column(Date, nullable=True)
    cover_image_url = Column(String(512), nullable=True)

    # External API tracking
    external_id = Column(String(100), nullable=True, index=True)
    external_source = Column(
        String(50), nullable=True
    )  # tmdb, jikan, igdb, openlibrary

    # Custom entry flag
    is_custom = Column(Boolean, default=False)

    # User ownership for custom entries
    created_by_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "media",
        "polymorphic_on": media_type,
        "with_polymorphic": "*",
    }

    # Relationships
    created_by = relationship("User", back_populates="created_media")
    tracking_entries = relationship(
        "Tracking", back_populates="media", cascade="all, delete-orphan"
    )
    tag_associations = relationship(
        "MediaTag", back_populates="media", cascade="all, delete-orphan"
    )
