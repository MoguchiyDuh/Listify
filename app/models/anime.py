from sqlalchemy import Column, Enum, ForeignKey, Integer, String

from .media import AnimeSeriesStatusEnum, Media, MediaTypeEnum


class Anime(Media):
    __tablename__ = "anime"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    total_episodes = Column(Integer, nullable=True)
    studio = Column(String(255), nullable=True)
    status = Column(
        Enum(AnimeSeriesStatusEnum),
        nullable=True,
        default=AnimeSeriesStatusEnum.FINISHED,
    )

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.ANIME,
    }

    def __repr__(self):
        return f"<Anime(id={self.id}, title={self.title})>"
