from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from apps.api.app.core.config import settings
from apps.api.app.core.database import get_db
from apps.api.app.core.errors import NotFoundError
from apps.api.app.api.v1.endpoints.auth import get_current_user_optional
from apps.api.app.models.user import User
from apps.api.app.models.report import AnalysisReport
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.report_service import report_service
from apps.api.app.services.storage_service import storage_service
from apps.api.app.schemas.reports import (
    ReportCreateRequest,
    ReportResponse,
    ReportListItem,
)

router = APIRouter(tags=["Rapports d'analyse"])


@router.post(
    "/analyses/{analysis_id}/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Générer un rapport horodaté et immuable",
)
def generate_report(
    analysis_id: UUID,
    payload: ReportCreateRequest = ReportCreateRequest(),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    """
    Creates an immutable snapshot of the analysis state, compiles the PDF,
    computes its SHA-256 hash, and saves the record.
    """
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    report = report_service.create_report(
        db=db,
        analysis=analysis,
        template_version=payload.template_version or "1.0.0",
    )

    return ReportResponse(
        id=report.id,
        analysis_id=report.analysis_id,
        report_version=report.report_version,
        template_version=report.template_version,
        snapshot_data=report.snapshot_data,
        pdf_sha256=report.pdf_sha256,
        pdf_download_url=f"/api/v1/reports/{report.id}/download",
        generated_at=report.generated_at,
        created_at=report.created_at,
    )


@router.get(
    "/analyses/{analysis_id}/reports",
    response_model=List[ReportListItem],
    summary="Lister les versions de rapport d'une analyse",
)
def list_analysis_reports(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    reports = db.execute(
        select(AnalysisReport)
        .where(AnalysisReport.analysis_id == analysis.id)
        .order_by(desc(AnalysisReport.report_version))
    ).scalars().all()

    return [
        ReportListItem(
            id=r.id,
            analysis_id=r.analysis_id,
            report_version=r.report_version,
            template_version=r.template_version,
            pdf_sha256=r.pdf_sha256,
            generated_at=r.generated_at,
        )
        for r in reports
    ]


@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    summary="Consulter le détail d'un rapport",
)
def get_report_detail(
    report_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    report = db.get(AnalysisReport, report_id)
    if not report:
        raise NotFoundError("Rapport", str(report_id))

    analysis = analysis_service.get_by_id_or_404(db, report.analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    return ReportResponse(
        id=report.id,
        analysis_id=report.analysis_id,
        report_version=report.report_version,
        template_version=report.template_version,
        snapshot_data=report.snapshot_data,
        pdf_sha256=report.pdf_sha256,
        pdf_download_url=f"/api/v1/reports/{report.id}/download",
        generated_at=report.generated_at,
        created_at=report.created_at,
    )


@router.get(
    "/reports/{report_id}/download",
    summary="Télécharger le fichier PDF immuable du rapport",
)
def download_report_pdf(
    report_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    report = db.get(AnalysisReport, report_id)
    if not report:
        raise NotFoundError("Rapport", str(report_id))

    analysis = analysis_service.get_by_id_or_404(db, report.analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    if not report.pdf_stored_object:
        raise NotFoundError("Fichier PDF du rapport", str(report_id))

    pdf_bytes = storage_service.download_file(
        report.pdf_stored_object.bucket_name,
        report.pdf_stored_object.storage_path,
    )

    filename = f"rapport_forensic_media_{analysis.public_id}_v{report.report_version}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
