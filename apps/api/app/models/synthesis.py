import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey, Index, Uuid
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import (
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    EvidenceType,
    EvidenceSeverity,
)


class SynthesisResult(Base):
    __tablename__ = "synthesis_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    conclusion_level = Column(SQLEnum(ConclusionLevel, native_enum=False), nullable=False)
    provenance_status = Column(SQLEnum(ProvenanceStatus, native_enum=False), nullable=False)
    integrity_status = Column(SQLEnum(IntegrityStatus, native_enum=False), nullable=False)
    ai_status = Column(SQLEnum(AIStatus, native_enum=False), nullable=False)
    context_status = Column(SQLEnum(ContextStatus, native_enum=False), nullable=False)

    summary_fr = Column(Text, nullable=False)
    synthesis_version = Column(String(50), default="1.0.0", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="synthesis_result")
    evidences = relationship("SynthesisEvidence", back_populates="synthesis", cascade="all, delete-orphan")


class SynthesisEvidence(Base):
    __tablename__ = "synthesis_evidence"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    synthesis_id = Column(Uuid, ForeignKey("synthesis_results.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)

    evidence_type = Column(SQLEnum(EvidenceType, native_enum=False), nullable=False)
    title_fr = Column(String(255), nullable=False)
    description_fr = Column(Text, nullable=False)
    source_engine = Column(String(50), nullable=False)
    severity = Column(
        SQLEnum(EvidenceSeverity, native_enum=False),
        default=EvidenceSeverity.INFO,
        nullable=False
    )
    reference_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    synthesis = relationship("SynthesisResult", back_populates="evidences")
    analysis = relationship("Analysis", back_populates="synthesis_evidences")


Index("idx_synthesis_evidence_type", SynthesisEvidence.analysis_id, SynthesisEvidence.evidence_type)
