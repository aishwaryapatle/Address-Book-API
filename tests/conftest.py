from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import Address  # noqa: F401


# Isolated in-memory database. StaticPool keeps the single
# connection alive so the schema survives across checkouts.
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create a clean database session for each test."""

    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client using the test database."""

    application = create_app(init_db=False)

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    application.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(application)

    try:
        yield test_client
    finally:
        test_client.close()
        application.dependency_overrides.clear()


@pytest.fixture
def sample_address() -> dict[str, object]:
    """Provide reusable address data for API tests."""

    return {
        "name": "Home",
        "street": "MG Road",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "postal_code": "411001",
        "latitude": 18.5204,
        "longitude": 73.8567,
    }
