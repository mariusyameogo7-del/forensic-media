from datetime import datetime, timezone
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.app.models.enums import (
    AnalysisStatus,
    EngineCode,
    EngineRunStatus,
    StoredObjectType,
)
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.engine_run import AnalysisEngineRun
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.results import (
    C2PAResult,
    MetadataResult,
    AIResult,
    WebMatch,
    FactCheckMatch,
)
from apps.api.app.models.synthesis import SynthesisResult, SynthesisEvidence
from apps.api.app.models.event import AnalysisEvent
from apps.api.app.services.storage_service import storage_service
from apps.api.app.services.cleanup_service import cleanup_service

from workers.analysis.worker.engines.hash_engine import HashEngine
from workers.analysis.worker.engines.metadata_engine import MetadataEngine
from workers.analysis.worker.engines.c2pa_engine import C2PAEngine
from workers.analysis.worker.engines.ai_engine import AIEngine
from workers.analysis.worker.engines.web_engine import WebEngine
from workers.analysis.worker.engines.factcheck_engine import FactCheckEngine
from workers.analysis.worker.engines.synthesis_engine import SynthesisEngine


class AnalysisOrchestrator:
    """
    Coordinates execution of all 6 engines and the final synthesis engine.
    Persists engine runs independently and handles partial provider outages gracefully.
    """

    def __init__(self):
        self.hash_engine = HashEngine()
        self.metadata_engine = MetadataEngine()
        self.c2pa_engine = C2PAEngine()
        self.ai_engine = AIEngine()
        self.web_engine = WebEngine()
        self.factcheck_engine = FactCheckEngine()
        self.synthesis_engine = SynthesisEngine()

    def process(self, db: Session, analysis_id: UUID) -> Analysis:
        analysis = db.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found.")

        # Update status to RUNNING
        analysis.status = AnalysisStatus.RUNNING
        db.commit()

        # Retrieve original file from storage
        orig_obj = db.execute(
            select(StoredObject).where(
                StoredObject.analysis_id == analysis.id,
                StoredObject.object_type == StoredObjectType.ORIGINAL,
                StoredObject.deleted_at.is_(None)
            )
        ).scalar_one_or_none()

        if not orig_obj:
            analysis.status = AnalysisStatus.FAILED
            analysis.error_code = "ORIGINAL_FILE_MISSING"
            analysis.public_error_message = "Le fichier original est introuvable."
            db.commit()
            return analysis

        file_bytes = storage_service.download_file(orig_obj.bucket_name, orig_obj.storage_path)

        # Load engine run records
        runs = {
            r.engine_code: r
            for r in db.execute(
                select(AnalysisEngineRun).where(AnalysisEngineRun.analysis_id == analysis.id)
            ).scalars().all()
        }

        # 1. Hashes Engine
        hash_res = None
        if EngineCode.HASHES in runs:
            st, hash_res, _ = self.hash_engine.execute_run(runs[EngineCode.HASHES], file_bytes)
            if st == EngineRunStatus.COMPLETED and hash_res:
                analysis.phash = hash_res.get("phash")
            db.commit()

        # 2. Metadata Engine
        meta_res = None
        if EngineCode.METADATA in runs:
            st, meta_res, _ = self.metadata_engine.execute_run(
                runs[EngineCode.METADATA],
                file_bytes=file_bytes,
                filename=analysis.original_filename
            )
            if st == EngineRunStatus.COMPLETED and meta_res:
                metadata_record = MetadataResult(
                    analysis_id=analysis.id,
                    engine_run_id=runs[EngineCode.METADATA].id,
                    make=meta_res.get("make"),
                    model=meta_res.get("model"),
                    software=meta_res.get("software"),
                    original_date=meta_res.get("original_date"),
                    modify_date=meta_res.get("modify_date"),
                    has_gps=meta_res.get("has_gps", False),
                    gps_latitude=meta_res.get("gps_latitude"),
                    gps_longitude=meta_res.get("gps_longitude"),
                    image_width=meta_res.get("image_width"),
                    image_height=meta_res.get("image_height"),
                    color_space=meta_res.get("color_space"),
                    raw_metadata=meta_res.get("raw_metadata"),
                )
                db.add(metadata_record)
            db.commit()

        # 3. C2PA Engine
        c2pa_res = None
        if EngineCode.C2PA in runs:
            st, c2pa_res, _ = self.c2pa_engine.execute_run(
                runs[EngineCode.C2PA],
                file_bytes=file_bytes,
                filename=analysis.original_filename
            )
            if st == EngineRunStatus.COMPLETED and c2pa_res:
                c2pa_record = C2PAResult(
                    analysis_id=analysis.id,
                    engine_run_id=runs[EngineCode.C2PA].id,
                    has_manifest=c2pa_res.get("has_manifest", False),
                    is_valid=c2pa_res.get("is_valid", False),
                    signature_status=c2pa_res.get("signature_status", "unknown"),
                    claim_generator=c2pa_res.get("claim_generator"),
                    issuer=c2pa_res.get("issuer"),
                    digital_source_type=c2pa_res.get("digital_source_type"),
                    ai_declared=c2pa_res.get("ai_declared", False),
                    actions=c2pa_res.get("actions"),
                    manifest_data=c2pa_res.get("manifest_data"),
                )
                db.add(c2pa_record)
            db.commit()

        # 4. AI Engine
        ai_res = None
        if EngineCode.AI in runs:
            st, ai_res, _ = self.ai_engine.execute_run(runs[EngineCode.AI], file_bytes=file_bytes)
            if st == EngineRunStatus.COMPLETED and ai_res:
                ai_record = AIResult(
                    analysis_id=analysis.id,
                    engine_run_id=runs[EngineCode.AI].id,
                    provider=ai_res.get("provider", "hive_ai"),
                    model_version=ai_res.get("model_version"),
                    raw_score=ai_res.get("raw_score"),
                    category=ai_res.get("category"),
                    confidence=ai_res.get("confidence"),
                    details=ai_res.get("details"),
                )
                db.add(ai_record)
            db.commit()

        # 5. Web Context Engine
        web_matches = []
        if EngineCode.WEB_CONTEXT in runs:
            st, web_res, _ = self.web_engine.execute_run(
                runs[EngineCode.WEB_CONTEXT],
                file_bytes=file_bytes,
                phash=analysis.phash,
                claim=analysis.claim
            )
            if st == EngineRunStatus.COMPLETED and web_res:
                for match in web_res:
                    match_rec = WebMatch(
                        analysis_id=analysis.id,
                        engine_run_id=runs[EngineCode.WEB_CONTEXT].id,
                        url=match.url,
                        domain=match.domain,
                        title=match.title,
                        match_type=match.match_type,
                        match_score=match.match_score,
                        earliest_date_found=match.earliest_date_found,
                        raw_payload=match.raw_payload,
                    )
                    db.add(match_rec)
                    web_matches.append(match_rec)
            db.commit()

        # 6. Fact Check Engine
        fact_checks = []
        if EngineCode.FACT_CHECK in runs:
            st, fc_res, _ = self.factcheck_engine.execute_run(
                runs[EngineCode.FACT_CHECK],
                claim=analysis.claim,
                web_matches=web_matches
            )
            if st == EngineRunStatus.COMPLETED and fc_res:
                for fc in fc_res:
                    fc_rec = FactCheckMatch(
                        analysis_id=analysis.id,
                        engine_run_id=runs[EngineCode.FACT_CHECK].id,
                        publisher_name=fc.publisher_name,
                        publisher_site=fc.publisher_site,
                        claim_reviewed=fc.claim_reviewed,
                        rating=fc.rating,
                        review_url=fc.review_url,
                        review_date=fc.review_date,
                        language=fc.language,
                        raw_payload=fc.raw_payload,
                    )
                    db.add(fc_rec)
                    fact_checks.append(fc_rec)
            db.commit()

        # 7. Synthesis Engine
        if EngineCode.SYNTHESIS in runs:
            runs[EngineCode.SYNTHESIS].status = EngineRunStatus.RUNNING
            runs[EngineCode.SYNTHESIS].started_at = datetime.now(timezone.utc)

            (
                conclusion_level,
                provenance_status,
                integrity_status,
                ai_status,
                context_status,
                summary_fr,
                evidences,
            ) = self.synthesis_engine.run(
                c2pa_data=c2pa_res,
                metadata_data=meta_res,
                hash_data=hash_res,
                ai_data=ai_res,
                web_matches=web_matches,
                fact_checks=fact_checks,
                claim=analysis.claim
            )

            # Persist synthesis result
            synth_record = SynthesisResult(
                analysis_id=analysis.id,
                conclusion_level=conclusion_level,
                provenance_status=provenance_status,
                integrity_status=integrity_status,
                ai_status=ai_status,
                context_status=context_status,
                summary_fr=summary_fr,
                synthesis_version="1.0.0",
            )
            db.add(synth_record)
            db.flush()

            # Persist synthesis evidence links
            for ev in evidences:
                ev_rec = SynthesisEvidence(
                    synthesis_id=synth_record.id,
                    analysis_id=analysis.id,
                    evidence_type=ev["evidence_type"],
                    title_fr=ev["title_fr"],
                    description_fr=ev["description_fr"],
                    source_engine=ev["source_engine"],
                    severity=ev["severity"],
                )
                db.add(ev_rec)

            # Update Analysis indicators & conclusion
            analysis.conclusion_level = conclusion_level
            analysis.provenance_status = provenance_status
            analysis.integrity_status = integrity_status
            analysis.ai_status = ai_status
            analysis.context_status = context_status
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.now(timezone.utc)

            runs[EngineCode.SYNTHESIS].status = EngineRunStatus.COMPLETED
            runs[EngineCode.SYNTHESIS].completed_at = datetime.now(timezone.utc)

            event = AnalysisEvent(
                analysis_id=analysis.id,
                event_type="synthesis_done",
                message=f"Synthèse terminée avec conclusion : '{conclusion_level.value}'.",
                metadata_json={"conclusion": conclusion_level.value}
            )
            db.add(event)
            db.commit()

        # Privacy Retention check (anonymous or user preference retain_original_files == False)
        should_retain = False
        if analysis.user and analysis.user.preferences:
            should_retain = analysis.user.preferences.retain_original_files

        if not should_retain:
            cleanup_service.cleanup_original_media(db, analysis.id)

        db.refresh(analysis)
        return analysis


orchestrator = AnalysisOrchestrator()
