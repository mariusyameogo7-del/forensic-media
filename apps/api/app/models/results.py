import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Index, Uuid, JSON
)
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import AIStatus, WebMatchType


class C2PAResult(Base):
    __tablename__ = "c2pa_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    engine_run_id = Column(Uuid, ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True)

    has_manifest = Column(Boolean, default=False, nullable=False)
    is_valid = Column(Boolean, default=False, nullable=False)
    signature_status = Column(String(50), default="unknown", nullable=False)
    claim_generator = Column(String(255), nullable=True)
    issuer = Column(String(255), nullable=True)
    digital_source_type = Column(String(255), nullable=True)
    ai_declared = Column(Boolean, default=False, nullable=False)
    actions = Column(JSON, nullable=True)
    manifest_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="c2pa_result")


class MetadataResult(Base):
    __tablename__ = "metadata_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    engine_run_id = Column(Uuid, ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True)

    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    software = Column(String(150), nullable=True)
    original_date = Column(DateTime(timezone=True), nullable=True)
    modify_date = Column(DateTime(timezone=True), nullable=True)
    has_gps = Column(Boolean, default=False, nullable=False)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    color_space = Column(String(50), nullable=True)
    raw_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="metadata_result")


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    engine_run_id = Column(Uuid, ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True)

    provider = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    raw_score = Column(Float, nullable=True)
    category = Column(
        SQLEnum(AIStatus, native_enum=False),
        default=AIStatus.INDETERMINATE,
        nullable=False
    )
    confidence = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="ai_result")


class WebMatch(Base):
    __tablename__ = "web_matches"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_run_id = Column(Uuid, ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True)

    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=True)
    title = Column(Text, nullable=True)
    match_type = Column(
        SQLEnum(WebMatchType, native_enum=False),
        default=WebMatchType.SIMILAR,
        nullable=False
    )
    match_score = Column(Float, nullable=True)
    earliest_date_found = Column(DateTime(timezone=True), nullable=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="web_matches")


class FactCheckMatch(Base):
    __tablename__ = "fact_check_matches"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    analysis_id = Column(Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_run_id = Column(Uuid, ForeignKey("analysis_engine_runs.id", ondelete="SET NULL"), nullable=True)

    publisher_name = Column(String(255), nullable=False)
    publisher_site = Column(String(255), nullable=True)
    claim_reviewed = Column(Text, nullable=False)
    rating = Column(String(100), nullable=False)
    review_url = Column(Text, nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    language = Column(String(20), nullable=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="fact_check_matches")
