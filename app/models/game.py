from enum import Enum

from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.models.media import Media, MediaTypeEnum


class PlatformEnum(str, Enum):
    PC = "pc"
    PS5 = "ps5"
    PS4 = "ps4"
    XBOX_SERIES = "xbox_series"
    XBOX_ONE = "xbox_one"
    SWITCH = "switch"
    MOBILE = "mobile"
    VR = "vr"


class Game(Media):
    __tablename__ = "games"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    platforms = Column(JSON, nullable=True)  # List of PlatformEnum values
    developer = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.GAME,
    }

    def __repr__(self):
        return f"<Game(id={self.id}, title={self.title})>"
