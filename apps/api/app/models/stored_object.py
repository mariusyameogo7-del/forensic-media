import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, BigInteger, DateTime, Enum as SQLEnum, ForeignKey, Index, Uuid
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import StoredObjectType


class StoredObject(Base):
    __tablename__ = "stored_objects"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    object_type = Column(SQLEnum(StoredObjectType, native_enum=False), nullable=False)
    bucket_name = Column(String(100), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    sha256 = Column(String(64), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="stored_objects")
    reports = relationship("AnalysisReport", back_populates="pdf_stored_object")


Index("idx_stored_objects_analysis_type", StoredObject.analysis_id, StoredObject.object_type)
