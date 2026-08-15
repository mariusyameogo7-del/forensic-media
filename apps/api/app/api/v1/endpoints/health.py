from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from apps.api.app.core.config import settings
from apps.api.app.core.database import get_db
from apps.api.app.schemas.common import HealthResponse

router = APIRouter(tags=["Santé"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Liveness probe."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/ready", response_model=HealthResponse)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking database connectivity."""
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="ready",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
