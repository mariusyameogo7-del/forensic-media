from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ReportCreateRequest(BaseModel):
    template_version: Optional[str] = "1.0.0"


class ReportResponse(BaseModel):
    id: UUID
    analysis_id: UUID
    report_version: int
    template_version: str
    snapshot_data: Dict[str, Any]
    pdf_sha256: Optional[str] = None
    pdf_download_url: Optional[str] = None
    generated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListItem(BaseModel):
    id: UUID
    analysis_id: UUID
    report_version: int
    template_version: str
    pdf_sha256: Optional[str] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
