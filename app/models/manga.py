from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String

from app.models.media import (AgeRatingEnum, Media, MediaStatusEnum,
                              MediaTypeEnum)


class Manga(Media):
    __tablename__ = "manga"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    original_title = Column(String(255), nullable=True)
    age_rating = Column(SQLEnum(AgeRatingEnum), nullable=True)
    total_chapters = Column(Integer, nullable=True)
    total_volumes = Column(Integer, nullable=True)
    author = Column(String(255), nullable=True)
    status = Column(SQLEnum(MediaStatusEnum), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.MANGA,
    }

    def __repr__(self):
        return f"<Manga(id={self.id}, title={self.title})>"
