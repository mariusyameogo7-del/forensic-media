from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, desc, asc, func

from apps.api.app.core.config import settings
from apps.api.app.core.errors import (
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
)
from apps.api.app.core.security import (
    generate_anonymous_token,
    generate_public_id,
    hash_token,
)
from apps.api.app.models.enums import (
    AnalysisStatus,
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    EngineCode,
    EngineRunStatus,
    StoredObjectType,
)
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.access_token import AnalysisAccessToken
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.engine_run import AnalysisEngineRun
from apps.api.app.models.event import AnalysisEvent
from apps.api.app.models.user import User
from apps.api.app.services.storage_service import storage_service
from apps.api.app.schemas.analysis import (
    AnalysisCreateResponse,
    AnalysisProgressResponse,
    EngineStepProgress,
    AnalysisResultResponse,
    EvidenceItem,
    AnalysisListItem,
)
from apps.api.app.schemas.common import PaginatedResponse


class AnalysisService:
    """Core analysis orchestration and database management service."""

    def create_analysis(
        self,
        db: Session,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        sha256_hash: str,
        phash_val: str,
        preview_bytes: bytes,
        claim: Optional[str] = None,
        user: Optional[User] = None,
    ) -> Tuple[Analysis, Optional[str]]:
        """
        Creates an analysis, persists stored_objects, creates engine run trackers,
        generates anonymous tokens if needed, logs events, and queues the celery job.
        """
        public_id = generate_public_id()
        user_id = user.id if user else None

        # 1. Create Analysis record
        analysis = Analysis(
            public_id=public_id,
            user_id=user_id,
            original_filename=filename,
            mime_type=mime_type,
            file_size=len(file_bytes),
            sha256=sha256_hash,
            phash=phash_val,
            claim=claim.strip() if claim else None,
            status=AnalysisStatus.PENDING,
        )
        db.add(analysis)
        db.flush()

        # 2. Handle Anonymous Access Token
        plain_token = None
        if user_id is None:
            plain_token, token_hash, expires_at = generate_anonymous_token()
            access_token_record = AnalysisAccessToken(
                analysis_id=analysis.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            db.add(access_token_record)

        # 3. Store Original File & Preview in Storage
        orig_storage_path = f"{analysis.id}/original_{filename}"
        storage_service.upload_file(
            bucket_name=settings.STORAGE_BUCKET_ORIGINALS,
            storage_path=orig_storage_path,
            data=file_bytes,
            content_type=mime_type,
        )
        stored_orig = StoredObject(
            analysis_id=analysis.id,
            object_type=StoredObjectType.ORIGINAL,
            bucket_name=settings.STORAGE_BUCKET_ORIGINALS,
            storage_path=orig_storage_path,
            mime_type=mime_type,
            file_size=len(file_bytes),
            sha256=sha256_hash,
        )
        db.add(stored_orig)

        preview_storage_path = f"{analysis.id}/preview.jpg"
        storage_service.upload_file(
            bucket_name=settings.STORAGE_BUCKET_PREVIEWS,
            storage_path=preview_storage_path,
            data=preview_bytes,
            content_type="image/jpeg",
        )
        stored_preview = StoredObject(
            analysis_id=analysis.id,
            object_type=StoredObjectType.PREVIEW,
            bucket_name=settings.STORAGE_BUCKET_PREVIEWS,
            storage_path=preview_storage_path,
            mime_type="image/jpeg",
            file_size=len(preview_bytes),
            sha256=storage_service.download_file(settings.STORAGE_BUCKET_PREVIEWS, preview_storage_path) and sha256_hash,
        )
        db.add(stored_preview)

        # 4. Initialize the 7 Engine Runs in analysis_engine_runs
        engine_configs = [
            (EngineCode.HASHES, "internal_hashlib", "1.0.0"),
            (EngineCode.METADATA, "exiftool", "13.59"),
            (EngineCode.C2PA, "c2pa-python", "0.37.7"),
            (EngineCode.AI, "hive_ai", "v2"),
            (EngineCode.WEB_CONTEXT, "google_vision", "v1"),
            (EngineCode.FACT_CHECK, "google_fact_check", "v1"),
            (EngineCode.SYNTHESIS, "forensic_synthesis", "1.0.0"),
        ]

        for code, provider, version in engine_configs:
            run = AnalysisEngineRun(
                analysis_id=analysis.id,
                engine_code=code,
                status=EngineRunStatus.PENDING,
                attempt_no=1,
                provider=provider,
                engine_version=version,
            )
            db.add(run)

        # 5. Log Business Audit Event
        event = AnalysisEvent(
            analysis_id=analysis.id,
            event_type="analysis_created",
            message=f"Analyse créée pour le fichier '{filename}' ({sha256_hash[:12]}...).",
            metadata_json={"claim_provided": bool(claim), "anonymous": user_id is None},
        )
        db.add(event)

        db.commit()
        db.refresh(analysis)

        # 6. Trigger Asynchronous Worker (celery task passing ONLY analysis_id)
        try:
            from workers.analysis.worker.tasks import process_analysis_task
            process_analysis_task.delay(str(analysis.id))
        except Exception:
            # If celery / redis isn't active in dev or unit tests, it can be triggered directly or in background
            pass

        return analysis, plain_token

    def verify_access(
        self,
        db: Session,
        analysis: Analysis,
        user: Optional[User] = None,
        raw_token: Optional[str] = None,
    ) -> bool:
        """
        Enforces strict authorization:
        1. If analysis has a user_id: requires matching authenticated user.
        2. If analysis is anonymous (user_id is None): requires valid hashed X-Analysis-Token.
        Note: public_id alone is NEVER sufficient for authorization.
        """
        if analysis.user_id is not None:
            if user is not None and user.id == analysis.user_id:
                return True
            raise ForbiddenError("Vous n'avez pas accès à cette analyse.")

        # Anonymous analysis
        if not raw_token:
            raise UnauthorizedError("Token d'accès 'X-Analysis-Token' requis pour cette analyse anonyme.")

        token_hash = hash_token(raw_token.strip())
        token_record = db.execute(
            select(AnalysisAccessToken).where(
                AnalysisAccessToken.analysis_id == analysis.id,
                AnalysisAccessToken.token_hash == token_hash,
            )
        ).scalar_one_or_none()

        if not token_record or not token_record.is_valid():
            raise UnauthorizedError("Token d'accès invalide ou expiré.")

        return True

    def get_by_id_or_404(self, db: Session, analysis_id: UUID) -> Analysis:
        analysis = db.get(Analysis, analysis_id)
        if not analysis:
            raise NotFoundError("Analyse", str(analysis_id))
        return analysis

    def get_progress(self, db: Session, analysis_id: UUID) -> AnalysisProgressResponse:
        """
        Returns real-time progress.
        IMPORTANT UX RULE: Never leaks partial findings before synthesis completion.
        """
        analysis = self.get_by_id_or_404(db, analysis_id)
        runs = db.execute(
            select(AnalysisEngineRun).where(AnalysisEngineRun.analysis_id == analysis.id)
        ).scalars().all()

        total_engines = len(runs) or 7
        completed_engines = sum(1 for r in runs if r.status in (EngineRunStatus.COMPLETED, EngineRunStatus.UNAVAILABLE, EngineRunStatus.NOT_APPLICABLE))
        
        progress_pct = int((completed_engines / total_engines) * 100) if total_engines else 0
        if analysis.status == AnalysisStatus.COMPLETED:
            progress_pct = 100

        current_running = next((r.engine_code.value for r in runs if r.status == EngineRunStatus.RUNNING), None)

        steps = [
            EngineStepProgress(
                engine_code=r.engine_code,
                status=r.status,
                started_at=r.started_at,
                completed_at=r.completed_at,
                duration_ms=r.duration_ms,
            )
            for r in runs
        ]

        return AnalysisProgressResponse(
            analysis_id=analysis.id,
            public_id=analysis.public_id,
            status=analysis.status,
            progress_percent=progress_pct,
            current_step=current_running,
            steps=steps,
            error_code=analysis.error_code,
            public_error_message=analysis.public_error_message,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
            completed_at=analysis.completed_at,
        )

    def get_result(self, db: Session, analysis_id: UUID) -> AnalysisResultResponse:
        """Returns the full synthesis and evidence results."""
        analysis = self.get_by_id_or_404(db, analysis_id)

        # Check if original file is still present or deleted for privacy
        orig_obj = db.execute(
            select(StoredObject).where(
                StoredObject.analysis_id == analysis.id,
                StoredObject.object_type == StoredObjectType.ORIGINAL,
                StoredObject.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

        evidences = [
            EvidenceItem(
                id=e.id,
                evidence_type=e.evidence_type,
                title_fr=e.title_fr,
                description_fr=e.description_fr,
                source_engine=e.source_engine,
                severity=e.severity,
                reference_id=e.reference_id,
            )
            for e in analysis.synthesis_evidences
        ]

        summary_text = analysis.synthesis_result.summary_fr if analysis.synthesis_result else None

        return AnalysisResultResponse(
            analysis_id=analysis.id,
            public_id=analysis.public_id,
            original_filename=analysis.original_filename,
            mime_type=analysis.mime_type,
            file_size=analysis.file_size,
            sha256=analysis.sha256,
            phash=analysis.phash,
            claim=analysis.claim,
            status=analysis.status,
            has_original_file=orig_obj is not None,
            conclusion_level=analysis.conclusion_level,
            provenance_status=analysis.provenance_status,
            integrity_status=analysis.integrity_status,
            ai_status=analysis.ai_status,
            context_status=analysis.context_status,
            summary_fr=summary_text,
            evidences=evidences,
            created_at=analysis.created_at,
            completed_at=analysis.completed_at,
        )

    def list_analyses(
        self,
        db: Session,
        user: Optional[User] = None,
        search: Optional[str] = None,
        conclusion: Optional[ConclusionLevel] = None,
        provenance: Optional[ProvenanceStatus] = None,
        ai: Optional[AIStatus] = None,
        context: Optional[ContextStatus] = None,
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[AnalysisListItem]:
        """Lists analyses with filters and pagination."""
        query = select(Analysis)

        if user:
            query = query.where(Analysis.user_id == user.id)
        else:
            # If unauthenticated, list empty unless specific tokens are queried
            return PaginatedResponse(items=[], total=0, page=page, page_size=page_size, has_more=False)

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Analysis.original_filename.ilike(search_pattern),
                    Analysis.public_id.ilike(search_pattern),
                    Analysis.claim.ilike(search_pattern),
                )
            )

        if conclusion:
            query = query.where(Analysis.conclusion_level == conclusion)
        if provenance:
            query = query.where(Analysis.provenance_status == provenance)
        if ai:
            query = query.where(Analysis.ai_status == ai)
        if context:
            query = query.where(Analysis.context_status == context)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar() or 0

        # Sort
        if sort_order.lower() == "asc":
            query = query.order_by(asc(Analysis.created_at))
        else:
            query = query.order_by(desc(Analysis.created_at))

        # Pagination
        offset = (page - 1) * page_size
        items = db.execute(query.offset(offset).limit(page_size)).scalars().all()

        list_items = []
        for a in items:
            has_orig = any(
                o.object_type == StoredObjectType.ORIGINAL and o.deleted_at is None
                for o in a.stored_objects
            )
            list_items.append(
                AnalysisListItem(
                    analysis_id=a.id,
                    public_id=a.public_id,
                    original_filename=a.original_filename,
                    file_size=a.file_size,
                    sha256=a.sha256,
                    claim_preview=(a.claim[:60] + "...") if a.claim and len(a.claim) > 60 else a.claim,
                    status=a.status,
                    has_original_file=has_orig,
                    conclusion_level=a.conclusion_level,
                    provenance_status=a.provenance_status,
                    integrity_status=a.integrity_status,
                    ai_status=a.ai_status,
                    context_status=a.context_status,
                    created_at=a.created_at,
                )
            )

        has_more = (offset + len(items)) < total
        return PaginatedResponse(
            items=list_items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more,
        )

    def delete_analysis(self, db: Session, analysis: Analysis) -> bool:
        """Deletes an analysis along with associated private storage objects."""
        # 1. Delete physical files from private storage
        for obj in analysis.stored_objects:
            storage_service.delete_file(obj.bucket_name, obj.storage_path)

        # 2. Delete database record (cascade will remove all children)
        db.delete(analysis)
        db.commit()
        return True


analysis_service = AnalysisService()
