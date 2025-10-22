import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String

from .media import Media, MediaTypeEnum


class PlatformEnum(str, enum.Enum):
    PC = "pc"
    PLAYSTATION = "playstation"
    XBOX = "xbox"
    NINTENDO = "nintendo"
    MOBILE = "mobile"
    WEB = "web"
    OTHER = "other"


class Game(Media):
    __tablename__ = "games"

    id = Column(Integer, ForeignKey("media.id"), primary_key=True)
    platform = Column(Enum(PlatformEnum), nullable=False, default=PlatformEnum.PC)
    developer = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    steam_id = Column(String(255), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": MediaTypeEnum.GAME,
    }

    def __repr__(self):
        return f"<Game(id={self.id}, title={self.title})>"
