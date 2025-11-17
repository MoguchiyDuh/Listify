from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String

from .media import AgeRatingEnum, Media, MediaStatusEnum, MediaTypeEnum


class Anime(Media):
    __tablename__ = "anime"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    original_title = Column(String(255), nullable=True)
    age_rating = Column(SQLEnum(AgeRatingEnum), nullable=True)
    seasons = Column(Integer, nullable=True)
    total_episodes = Column(Integer, nullable=True)
    studios = Column(JSON, nullable=True)  # List of studio names
    status = Column(SQLEnum(MediaStatusEnum), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.ANIME,
    }

    def __repr__(self):
        return f"<Anime(id={self.id}, title={self.title})>"
