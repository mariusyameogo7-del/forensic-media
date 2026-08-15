import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SQLEnum, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import EngineCode, EngineRunStatus


class AnalysisEngineRun(Base):
    __tablename__ = "analysis_engine_runs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_code = Column(SQLEnum(EngineCode, native_enum=False), nullable=False)
    status = Column(
        SQLEnum(EngineRunStatus, native_enum=False),
        default=EngineRunStatus.PENDING,
        nullable=False,
        index=True
    )
    attempt_no = Column(Integer, default=1, nullable=False)
    provider = Column(String(100), nullable=False)
    engine_version = Column(String(50), nullable=True)
    provider_version = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_code = Column(String(100), nullable=True)
    public_error_message = Column(Text, nullable=True)
    private_error_details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="engine_runs")


Index("idx_engine_runs_analysis_engine", AnalysisEngineRun.analysis_id, AnalysisEngineRun.engine_code)
