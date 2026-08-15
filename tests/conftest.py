import pytest
import io
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from apps.api.app.core.database import Base, get_db
from apps.api.app.main import app
import apps.api.app.models

# In-memory SQLite for super-fast, deterministic unit tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_valid_jpeg() -> bytes:
    """Generates a small valid JPEG in bytes."""
    img = Image.new("RGB", (200, 200), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def sample_valid_png() -> bytes:
    """Generates a small valid PNG in bytes."""
    img = Image.new("RGBA", (150, 150), color=(255, 0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_valid_webp() -> bytes:
    """Generates a small valid WebP in bytes."""
    img = Image.new("RGB", (100, 100), color=(0, 255, 100))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    return buf.getvalue()
