"""
Pytest configuration and test database isolation fixture for CloudRoute AI.
Uses an in-memory SQLite database to ensure each test runs against a clean,
isolated database without mutating or depending on local sqlite files.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


@pytest.fixture(autouse=True)
def isolated_test_db():
    """
    Creates a fresh, isolated in-memory SQLite database for each test execution,
    guaranteeing test repeatability and clean initial states.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
