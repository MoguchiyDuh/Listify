from sqlalchemy import JSON, Column, ForeignKey, Integer

from .media import Media, MediaTypeEnum


class Movie(Media):
    __tablename__ = "movies"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    runtime = Column(Integer, nullable=True)  # in minutes
    directors = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.MOVIE,
    }

    def __repr__(self):
        return f"<Movie(id={self.id}, title={self.title})>"
