from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from apps.api.app.models.enums import AIStatus, WebMatchType, EvidenceType, EvidenceSeverity


class C2PAResponse(BaseModel):
    analysis_id: UUID
    has_manifest: bool
    is_valid: bool
    signature_status: str
    claim_generator: Optional[str] = None
    issuer: Optional[str] = None
    digital_source_type: Optional[str] = None
    ai_declared: bool
    actions: Optional[List[Dict[str, Any]]] = None
    manifest_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetadataResponse(BaseModel):
    analysis_id: UUID
    make: Optional[str] = None
    model: Optional[str] = None
    software: Optional[str] = None
    original_date: Optional[datetime] = None
    modify_date: Optional[datetime] = None
    has_gps: bool
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    color_space: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIResultResponse(BaseModel):
    analysis_id: UUID
    provider: str
    model_version: Optional[str] = None
    category: AIStatus
    confidence: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebMatchItem(BaseModel):
    id: UUID
    url: str
    domain: Optional[str] = None
    title: Optional[str] = None
    match_type: WebMatchType
    match_score: Optional[float] = None
    earliest_date_found: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WebMatchesResponse(BaseModel):
    analysis_id: UUID
    matches_count: int
    matches: List[WebMatchItem]

    model_config = ConfigDict(from_attributes=True)


class FactCheckItem(BaseModel):
    id: UUID
    publisher_name: str
    publisher_site: Optional[str] = None
    claim_reviewed: str
    rating: str
    review_url: str
    review_date: Optional[datetime] = None
    language: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FactChecksResponse(BaseModel):
    analysis_id: UUID
    matches_count: int
    matches: List[FactCheckItem]

    model_config = ConfigDict(from_attributes=True)


class EvidenceListResponse(BaseModel):
    analysis_id: UUID
    evidence_count: int
    items: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
