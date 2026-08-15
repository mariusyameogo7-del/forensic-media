from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File, Form, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from apps.api.app.core.database import get_db
from apps.api.app.core.errors import InvalidFileError
from apps.api.app.api.v1.endpoints.auth import get_current_user_optional, get_current_user
from apps.api.app.models.user import User
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.access_token import AnalysisAccessToken
from apps.api.app.models.enums import AnalysisStatus, ConclusionLevel
from apps.api.app.schemas.analysis import (
    AnalysisCreateResponse,
    AnalysisProgressResponse,
    EngineStepProgress,
    AnalysisListResponse,
    AnalysisListItem,
)
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from workers.analysis.worker.tasks import process_analysis_task
from workers.analysis.worker.orchestrator import orchestrator

router = APIRouter()


@router.post(
    "/analyses",
    response_model=AnalysisCreateResponse,
    status_code=201,
    summary="Soumettre un nouveau média pour analyse",
)
async def create_analysis(
    file: UploadFile = File(...),
    claim: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    file_bytes = await file.read()
    if not file_bytes:
        raise InvalidFileError("Le fichier envoyé est vide.")

    # 1. Validation & Processing
    mime_type, sha256_hash, phash_val, filename, preview_bytes = upload_service.validate_and_process(
        file_bytes=file_bytes,
        filename=file.filename or "media_file",
        content_type=file.content_type,
    )

    # 2. Database Record & Initial Runs Creation
    analysis, plain_token = analysis_service.create_analysis(
        db=db,
        file_bytes=file_bytes,
        filename=filename,
        mime_type=mime_type,
        sha256_hash=sha256_hash,
        phash_val=phash_val,
        preview_bytes=preview_bytes,
        claim=claim,
        user=current_user,
    )

    # 3. Enqueue Celery Task / Fallback to direct synchronous execution
    try:
        process_analysis_task.delay(str(analysis.id))
    except Exception:
        orchestrator.process(db, analysis.id)

    return AnalysisCreateResponse(
        analysis_id=analysis.id,
        public_id=analysis.public_id,
        status=analysis.status,
        original_filename=analysis.original_filename,
        file_size=analysis.file_size,
        sha256=analysis.sha256,
        access_token=plain_token,
        progress_url=f"/api/v1/analyses/{analysis.id}/progress",
        created_at=analysis.created_at,
    )


@router.get(
    "/analyses/{analysis_id}/progress",
    response_model=AnalysisProgressResponse,
    summary="Consulter l'état d'avancement technique de l'analyse",
)
def get_analysis_progress(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_analysis_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=current_user, raw_token=x_analysis_token)

    total_runs = len(analysis.engine_runs)
    completed_runs = sum(
        1 for r in analysis.engine_runs if r.status.value in ("completed", "failed", "skipped")
    )
    progress_percent = int((completed_runs / total_runs) * 100) if total_runs > 0 else 0

    engine_items = [
        EngineStepProgress(
            engine_code=r.engine_code,
            status=r.status,
            started_at=r.started_at,
            completed_at=r.completed_at,
            duration_ms=r.duration_ms,
        )
        for r in analysis.engine_runs
    ]

    return AnalysisProgressResponse(
        analysis_id=analysis.id,
        public_id=analysis.public_id,
        status=analysis.status,
        progress_percent=progress_percent,
        current_step=None,
        steps=engine_items,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        completed_at=analysis.completed_at,
    )


@router.get(
    "/analyses",
    response_model=AnalysisListResponse,
    summary="Lister l'historique des analyses",
)
def list_analyses(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conclusion: Optional[ConclusionLevel] = Query(None),
    status: Optional[AnalysisStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    query = select(Analysis)

    if current_user:
        query = query.where(Analysis.user_id == current_user.id)
    
    if conclusion:
        query = query.where(Analysis.conclusion_level == conclusion)
    if status:
        query = query.where(Analysis.status == status)
    if search:
        query = query.where(
            (Analysis.original_filename.ilike(f"%{search}%"))
            | (Analysis.public_id.ilike(f"%{search}%"))
            | (Analysis.claim.ilike(f"%{search}%"))
        )

    query = query.order_by(desc(Analysis.created_at))

    total = len(db.execute(query).scalars().all())
    items = db.execute(query.offset(offset).limit(limit)).scalars().all()

    list_items = [
        AnalysisListItem(
            analysis_id=a.id,
            public_id=a.public_id,
            original_filename=a.original_filename,
            file_size=a.file_size,
            sha256=a.sha256,
            claim_preview=(a.claim[:80] + "...") if a.claim and len(a.claim) > 80 else a.claim,
            status=a.status,
            has_original_file=True,
            conclusion_level=a.conclusion_level,
            provenance_status=a.provenance_status,
            integrity_status=a.integrity_status,
            ai_status=a.ai_status,
            context_status=a.context_status,
            created_at=a.created_at,
        )
        for a in items
    ]

    return AnalysisListResponse(items=list_items, total=total, limit=limit, offset=offset)
