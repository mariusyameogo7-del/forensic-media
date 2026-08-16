from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from apps.api.app.models.enums import (
    AnalysisStatus,
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    EngineRunStatus,
    EngineCode,
    EvidenceType,
    EvidenceSeverity,
)


class AnalysisCreateResponse(BaseModel):
    analysis_id: UUID
    public_id: str
    status: AnalysisStatus
    original_filename: str
    file_size: int
    sha256: str
    access_token: Optional[str] = None # Returned only once to anonymous creators
    progress_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EngineStepProgress(BaseModel):
    engine_code: EngineCode
    status: EngineRunStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisProgressResponse(BaseModel):
    analysis_id: UUID
    public_id: str
    status: AnalysisStatus
    progress_percent: int
    current_step: Optional[str] = None
    steps: List[EngineStepProgress] = []
    error_code: Optional[str] = None
    public_error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceItem(BaseModel):
    id: UUID
    evidence_type: EvidenceType
    title_fr: str
    description_fr: str
    source_engine: str
    severity: EvidenceSeverity
    reference_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class IndicatorsSummary(BaseModel):
    conclusion_level: ConclusionLevel
    provenance: ProvenanceStatus
    integrity: IntegrityStatus
    ai: AIStatus
    context: ContextStatus


class CameraMetadataDetails(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    software: Optional[str] = None
    lens_model: Optional[str] = None
    iso: Optional[int] = None
    exposure_time: Optional[str] = None
    f_number: Optional[float] = None
    focal_length: Optional[float] = None
    date_time_original: Optional[datetime] = None
    has_gps: bool = False
    raw_details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class WebMatchItem(BaseModel):
    url: str
    domain: str
    title: Optional[str] = None
    match_score: Optional[float] = None
    earliest_date_found: Optional[datetime] = None
    source_platform: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FactCheckMatchItem(BaseModel):
    publisher_name: str
    publisher_site: str
    claim_reviewed: str
    rating: str
    review_url: str
    review_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class C2PADetails(BaseModel):
    has_manifest: bool = False
    is_valid: bool = False
    issuer: Optional[str] = None
    claim_generator: Optional[str] = None
    digital_source_type: Optional[str] = None
    ai_declared: bool = False
    cert_info: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisResultResponse(BaseModel):
    analysis_id: UUID
    public_id: str
    original_filename: str
    mime_type: str
    file_size: int
    sha256: str
    phash: Optional[str] = None
    claim: Optional[str] = None
    status: AnalysisStatus
    has_original_file: bool = True
    
    # 4 independent indicators + conclusion
    conclusion_level: Optional[ConclusionLevel] = None
    provenance_status: Optional[ProvenanceStatus] = None
    integrity_status: Optional[IntegrityStatus] = None
    ai_status: Optional[AIStatus] = None
    context_status: Optional[ContextStatus] = None
    
    # Precise AI Probabilities & C2PA Provenance Scores
    ai_probability_score: Optional[float] = None # 0.0 to 1.0 (ex: 0.98 -> 98%)
    ai_confidence_score: Optional[float] = None # 0.0 to 1.0 (ex: 0.99 -> 99%)
    ai_generator_name: Optional[str] = None # ex: "OpenAI DALL·E 3 (ChatGPT)"
    provenance_issuer: Optional[str] = None # ex: "OpenAI, LLC"
    c2pa_valid: Optional[bool] = None
    c2pa_digital_source: Optional[str] = None
    
    # Deep Technical Breakdown
    camera_metadata: Optional[CameraMetadataDetails] = None
    web_occurrences: List[WebMatchItem] = []
    fact_check_debunks: List[FactCheckMatchItem] = []
    c2pa_details: Optional[C2PADetails] = None
    
    summary_fr: Optional[str] = None
    evidences: List[EvidenceItem] = []
    
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisListItem(BaseModel):
    analysis_id: UUID
    public_id: str
    original_filename: str
    file_size: int
    sha256: str
    claim_preview: Optional[str] = None
    status: AnalysisStatus
    has_original_file: bool
    conclusion_level: Optional[ConclusionLevel] = None
    provenance_status: Optional[ProvenanceStatus] = None
    integrity_status: Optional[IntegrityStatus] = None
    ai_status: Optional[AIStatus] = None
    context_status: Optional[ContextStatus] = None
    ai_probability_score: Optional[float] = None
    ai_generator_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisListResponse(BaseModel):
    items: List[AnalysisListItem]
    total: int
    limit: int
    offset: int
