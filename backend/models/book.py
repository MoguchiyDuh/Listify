from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from .media import Media, MediaTypeEnum


class Book(Media):
    __tablename__ = "books"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    pages = Column(Integer, nullable=True)
    authors = Column(JSON, nullable=True)
    isbn = Column(String(20), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.BOOK,
    }

    def __repr__(self):
        return f"<Book(id={self.id}:, title={self.title})>"
