import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base


class AnalysisEvent(Base):
    __tablename__ = "analysis_events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    message = Column(String(255), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="events")


Index("idx_analysis_events_created", AnalysisEvent.analysis_id, AnalysisEvent.created_at)
