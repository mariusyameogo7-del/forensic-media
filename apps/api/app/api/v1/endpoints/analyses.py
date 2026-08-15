from typing import Optional
from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    Header,
    Query,
    status,
)
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.api.v1.endpoints.auth import get_current_user_optional, get_current_user
from apps.api.app.models.user import User
from apps.api.app.models.enums import (
    ConclusionLevel,
    ProvenanceStatus,
    AIStatus,
    ContextStatus,
)
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.schemas.analysis import (
    AnalysisCreateResponse,
    AnalysisProgressResponse,
    AnalysisResultResponse,
    AnalysisListItem,
)
from apps.api.app.schemas.common import PaginatedResponse

router = APIRouter(tags=["Analyses"])


@router.post(
    "/analyses",
    response_model=AnalysisCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Créer et lancer une analyse d'image",
)
async def create_analysis(
    file: UploadFile = File(..., description="Fichier image (JPG, JPEG, PNG, WEBP, max 20 MiB)"),
    claim: Optional[str] = Form(None, description="Affirmation facultative associée à l'image"),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Receives an image file, validates MIME and binary signature, calculates SHA-256 and pHash,
    stores the media in private storage, initiates the 7 engine runs, and enqueues asynchronous analysis.
    """
    file_bytes = await file.read()
    filename = file.filename or "upload.jpg"

    # Validation and Hash computation
    mime_type, sha256_hash, phash_val, norm_filename, preview_bytes = upload_service.validate_and_process(
        file_bytes=file_bytes,
        filename=filename,
        content_type=file.content_type,
    )

    analysis, plain_token = analysis_service.create_analysis(
        db=db,
        file_bytes=file_bytes,
        filename=norm_filename,
        mime_type=mime_type,
        sha256_hash=sha256_hash,
        phash_val=phash_val,
        preview_bytes=preview_bytes,
        claim=claim,
        user=user,
    )

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
    summary="Consulter l'avancement de l'analyse (Polling HTTP)",
)
def get_analysis_progress(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    """
    Pollable endpoint reporting real-time progress.
    Strictly forbids leaking partial conclusions before synthesis is completed.
    """
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)
    return analysis_service.get_progress(db, analysis_id)


@router.get(
    "/analyses/{analysis_id}",
    response_model=AnalysisResultResponse,
    summary="Détail d'une analyse",
)
def get_analysis_detail(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    """Returns the analysis overview, status, and synthesis."""
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)
    return analysis_service.get_result(db, analysis_id)


@router.get(
    "/analyses",
    response_model=PaginatedResponse[AnalysisListItem],
    summary="Historique des analyses de l'utilisateur",
)
def list_analyses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Recherche par nom, public_id ou affirmation"),
    conclusion: Optional[ConclusionLevel] = Query(None, description="Filtre par conclusion"),
    provenance: Optional[ProvenanceStatus] = Query(None, description="Filtre par provenance"),
    ai: Optional[AIStatus] = Query(None, description="Filtre par indice IA"),
    context: Optional[ContextStatus] = Query(None, description="Filtre par contexte"),
    sort: str = Query("desc", enum=["asc", "desc"], description="Ordre de tri temporel"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Lists analyses belonging to the authenticated user with multi-dimensional filters."""
    return analysis_service.list_analyses(
        db=db,
        user=user,
        search=search,
        conclusion=conclusion,
        provenance=provenance,
        ai=ai,
        context=context,
        sort_order=sort,
        page=page,
        page_size=page_size,
    )


@router.delete(
    "/analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une analyse et ses fichiers associés",
)
def delete_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    """Deletes the analysis and triggers private storage cleanup."""
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)
    analysis_service.delete_analysis(db, analysis)
    return None
