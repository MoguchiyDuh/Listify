import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import Base
from app.models import *


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    from app.crud import user_crud

    user = user_crud.create(
        db_session,
        username="testuser",
        email="test@example.com",
        password="testpassword123",
    )
    return user


@pytest.fixture
def sample_movie(db_session):
    """Create a sample movie for testing"""
    from datetime import date

    from app.crud import media_crud
    from app.schemas.movie import MovieCreate

    movie_data = MovieCreate(
        title="Test Movie",
        description="A test movie",
        release_date=date(2020, 1, 1),
        runtime=120,
        tags=["Action", "Sci-Fi"],
    )

    return media_crud.create_movie(db_session, obj_in=movie_data)


@pytest.fixture
def sample_anime(db_session):
    """Create a sample anime for testing"""
    from app.crud import media_crud
    from app.models import AgeRatingEnum, MediaStatusEnum
    from app.schemas.anime import AnimeCreate

    anime_data = AnimeCreate(
        title="Test Anime",
        original_title="テストアニメ",
        description="A test anime",
        total_episodes=12,
        studios=["Test Studio"],
        status=MediaStatusEnum.FINISHED,
        age_rating=AgeRatingEnum.PG_13,
        tags=["Action", "Fantasy"],
    )

    return media_crud.create_anime(db_session, obj_in=anime_data)


@pytest.fixture
def sample_game(db_session):
    """Create a sample game for testing"""
    from app.crud import media_crud
    from app.models import PlatformEnum
    from app.schemas.game import GameCreate

    game_data = GameCreate(
        title="Test Game",
        description="A test game",
        platforms=[PlatformEnum.PC],
        developer="Test Developer",
        publisher="Test Publisher",
        tags=["RPG", "Adventure"],
    )

    return media_crud.create_game(db_session, obj_in=game_data)
