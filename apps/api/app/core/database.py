import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from apps.api.app.core.config import settings

def get_engine():
    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    try:
        eng = create_engine(
            db_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2} if "postgresql" in db_url else {}
        )
        with eng.connect():
            pass
        return eng
    except Exception:
        # Fallback to local SQLite database for instant standalone testing
        sqlite_url = "sqlite:///forensic_media_demo.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, future=True)

engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
