import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    report_version = Column(Integer, default=1, nullable=False)
    template_version = Column(String(50), default="1.0.0", nullable=False)
    
    snapshot_data = Column(JSON, nullable=False)
    
    pdf_stored_object_id = Column(Uuid, ForeignKey("stored_objects.id", ondelete="SET NULL"), nullable=True)
    pdf_sha256 = Column(String(64), nullable=True)
    
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="reports")
    pdf_stored_object = relationship("StoredObject", back_populates="reports")


Index("idx_analysis_reports_version", AnalysisReport.analysis_id, AnalysisReport.report_version)
