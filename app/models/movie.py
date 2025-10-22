from sqlalchemy import Column, ForeignKey, Integer, String

from .media import Media, MediaTypeEnum


class Movie(Media):
    __tablename__ = "movies"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    runtime = Column(Integer, nullable=True)  # Minutes
    director = Column(String(255), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.MOVIE,
    }

    def __repr__(self):
        return f"<Movie(id={self.id}, title={self.title})>"
