import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from apps.api.app.core.config import settings

Base = declarative_base()


def get_engine():
    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    
    # Ensure psycopg v3 dialect is used for PostgreSQL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    try:
        eng = create_engine(
            db_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5} if "postgresql" in db_url else {}
        )
        with eng.connect():
            pass
        return eng
    except Exception as e:
        print("[DATABASE FALLBACK TO SQLITE]:", e)
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


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
