import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


# Shared test engine — StaticPool ensures all connections use the same in-memory DB
engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine_test)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    """Provide a clean DB session for unit tests (non-route tests)."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db_and_authenticate():
    """Create tables and authenticate before each test, drop tables after."""
    Base.metadata.create_all(bind=engine_test)
    from app.config import settings
    client.post("/login", data={
        "username": settings.auth_username,
        "password": settings.auth_password,
    })
    yield
    Base.metadata.drop_all(bind=engine_test)
