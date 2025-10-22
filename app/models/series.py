from sqlalchemy import Column, Enum, ForeignKey, Integer

from .media import AnimeSeriesStatusEnum, Media, MediaTypeEnum


class Series(Media):
    __tablename__ = "series"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    total_episodes = Column(Integer, nullable=True)
    seasons = Column(Integer, nullable=True)
    status = Column(
        Enum(AnimeSeriesStatusEnum),
        nullable=True,
        default=AnimeSeriesStatusEnum.FINISHED,
    )

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.SERIES,
    }

    def __repr__(self):
        return f"<Series(id={self.id}, title={self.title})>"
