import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.database import Base


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    test_db_url = "sqlite:///./test.db"
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up test database file
    if Path("test.db").exists():
        Path("test.db").unlink()


@pytest.fixture(scope="function")
def db(engine) -> Generator[Session, None, None]:
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def clean_db(engine) -> Generator[Session, None, None]:
    """Create clean database session and clear all data after test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    # Clear all tables
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
