import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, Index, Uuid
)
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import (
    AnalysisStatus,
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    public_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    sha256 = Column(String(64), nullable=False, index=True)
    phash = Column(String(64), nullable=True, index=True)
    claim = Column(Text, nullable=True)

    # Technical processing status
    status = Column(
        SQLEnum(AnalysisStatus, native_enum=False),
        default=AnalysisStatus.PENDING,
        nullable=False,
        index=True
    )

    # Synthesis conclusion & 4 independent indicators
    conclusion_level = Column(SQLEnum(ConclusionLevel, native_enum=False), nullable=True)
    provenance_status = Column(SQLEnum(ProvenanceStatus, native_enum=False), nullable=True)
    integrity_status = Column(SQLEnum(IntegrityStatus, native_enum=False), nullable=True)
    ai_status = Column(SQLEnum(AIStatus, native_enum=False), nullable=True)
    context_status = Column(SQLEnum(ContextStatus, native_enum=False), nullable=True)

    error_code = Column(String(100), nullable=True)
    public_error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="analyses")
    access_tokens = relationship("AnalysisAccessToken", back_populates="analysis", cascade="all, delete-orphan")
    stored_objects = relationship("StoredObject", back_populates="analysis", cascade="all, delete-orphan")
    engine_runs = relationship("AnalysisEngineRun", back_populates="analysis", cascade="all, delete-orphan")
    c2pa_result = relationship("C2PAResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    metadata_result = relationship("MetadataResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    ai_result = relationship("AIResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    web_matches = relationship("WebMatch", back_populates="analysis", cascade="all, delete-orphan")
    fact_check_matches = relationship("FactCheckMatch", back_populates="analysis", cascade="all, delete-orphan")
    synthesis_result = relationship("SynthesisResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    synthesis_evidences = relationship("SynthesisEvidence", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("AnalysisReport", back_populates="analysis", cascade="all, delete-orphan")
    events = relationship("AnalysisEvent", back_populates="analysis", cascade="all, delete-orphan")


Index("idx_analyses_user_created", Analysis.user_id, Analysis.created_at.desc())
