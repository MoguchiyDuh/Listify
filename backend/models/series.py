from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer

from .media import Media, MediaStatusEnum, MediaTypeEnum


class Series(Media):
    __tablename__ = "series"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    total_episodes = Column(Integer, nullable=True)
    seasons = Column(Integer, nullable=True)
    status = Column(SQLEnum(MediaStatusEnum), nullable=True)
    directors = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.SERIES,
    }

    def __repr__(self):
        return f"<Series(id={self.id}, title={self.title})>"
