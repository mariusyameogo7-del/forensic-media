from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.app.core.config import settings
from apps.api.app.core.database import get_db
from apps.api.app.core.errors import NotFoundError
from apps.api.app.api.v1.endpoints.auth import get_current_user_optional
from apps.api.app.models.user import User
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.enums import StoredObjectType
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.storage_service import storage_service
from apps.api.app.schemas.analysis import AnalysisResultResponse
from apps.api.app.schemas.results import (
    C2PAResponse,
    MetadataResponse,
    AIResultResponse,
    WebMatchesResponse,
    WebMatchItem,
    FactChecksResponse,
    FactCheckItem,
    EvidenceListResponse,
)

router = APIRouter(tags=["Résultats d'analyse"])


@router.get(
    "/analyses/{analysis_id}/result",
    response_model=AnalysisResultResponse,
    summary="Résultat complet et synthèse de l'analyse",
)
def get_full_result(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)
    return analysis_service.get_result(db, analysis_id)


@router.get(
    "/analyses/{analysis_id}/evidence",
    response_model=EvidenceListResponse,
    summary="Éléments de preuve justifiant la conclusion",
)
def get_analysis_evidence(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    evidences = [
        {
            "id": str(e.id),
            "evidence_type": e.evidence_type.value,
            "title_fr": e.title_fr,
            "description_fr": e.description_fr,
            "source_engine": e.source_engine,
            "severity": e.severity.value,
            "reference_id": e.reference_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in analysis.synthesis_evidences
    ]

    return EvidenceListResponse(
        analysis_id=analysis.id,
        evidence_count=len(evidences),
        items=evidences,
    )


@router.get(
    "/analyses/{analysis_id}/c2pa",
    response_model=Optional[C2PAResponse],
    summary="Détails du moteur C2PA / Content Credentials",
)
def get_c2pa_details(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    if not analysis.c2pa_result:
        raise NotFoundError("Résultat C2PA", str(analysis_id))

    return C2PAResponse.model_validate(analysis.c2pa_result)


@router.get(
    "/analyses/{analysis_id}/metadata",
    response_model=Optional[MetadataResponse],
    summary="Détails du moteur Métadonnées (ExifTool)",
)
def get_metadata_details(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    if not analysis.metadata_result:
        raise NotFoundError("Résultat Métadonnées", str(analysis_id))

    return MetadataResponse.model_validate(analysis.metadata_result)


@router.get(
    "/analyses/{analysis_id}/ai",
    response_model=Optional[AIResultResponse],
    summary="Détails du moteur d'estimation IA",
)
def get_ai_details(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    if not analysis.ai_result:
        raise NotFoundError("Résultat IA", str(analysis_id))

    return AIResultResponse.model_validate(analysis.ai_result)


@router.get(
    "/analyses/{analysis_id}/web-matches",
    response_model=WebMatchesResponse,
    summary="Correspondances Web et antériorités retrouvées",
)
def get_web_matches(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    matches = [
        WebMatchItem(
            id=m.id,
            url=m.url,
            domain=m.domain,
            title=m.title,
            match_type=m.match_type,
            match_score=m.match_score,
            earliest_date_found=m.earliest_date_found,
        )
        for m in analysis.web_matches
    ]

    return WebMatchesResponse(
        analysis_id=analysis.id,
        matches_count=len(matches),
        matches=matches,
    )


@router.get(
    "/analyses/{analysis_id}/fact-checks",
    response_model=FactChecksResponse,
    summary="Fact-checks existants identifiés",
)
def get_fact_checks(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    matches = [
        FactCheckItem(
            id=m.id,
            publisher_name=m.publisher_name,
            publisher_site=m.publisher_site,
            claim_reviewed=m.claim_reviewed,
            rating=m.rating,
            review_url=m.review_url,
            review_date=m.review_date,
            language=m.language,
        )
        for m in analysis.fact_check_matches
    ]

    return FactChecksResponse(
        analysis_id=analysis.id,
        matches_count=len(matches),
        matches=matches,
    )


@router.get(
    "/analyses/{analysis_id}/preview",
    summary="Télécharger ou afficher l'aperçu de l'image analysée",
)
def get_image_preview(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
    x_analysis_token: Optional[str] = Header(None, alias="X-Analysis-Token"),
):
    analysis = analysis_service.get_by_id_or_404(db, analysis_id)
    analysis_service.verify_access(db, analysis, user=user, raw_token=x_analysis_token)

    preview_obj = db.execute(
        select(StoredObject).where(
            StoredObject.analysis_id == analysis.id,
            StoredObject.object_type.in_([StoredObjectType.PREVIEW, StoredObjectType.ORIGINAL]),
            StoredObject.deleted_at.is_(None),
        )
    ).scalars().first()

    if not preview_obj:
        raise NotFoundError("Aperçu (fichier supprimé pour confidentialité)", str(analysis_id))

    file_bytes = storage_service.download_file(preview_obj.bucket_name, preview_obj.storage_path)
    return Response(content=file_bytes, media_type=preview_obj.mime_type)
