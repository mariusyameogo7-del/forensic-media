import pytest
from uuid import UUID
from apps.api.app.models.enums import (
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    WebMatchType,
)
from workers.analysis.worker.engines.synthesis_engine import SynthesisEngine
from workers.analysis.worker.adapters.base import WebMatchResult, FactCheckResult
from workers.analysis.worker.orchestrator import orchestrator


def test_synthesis_engine_clear_indicators():
    engine = SynthesisEngine()
    
    metadata = {"make": "Canon", "model": "EOS 5D", "software": "v1.0"}
    c2pa = {"has_manifest": True, "is_valid": True, "claim_generator": "Adobe Photoshop"}
    ai = {"category": AIStatus.LOW, "raw_score": 0.05}
    
    (
        conclusion,
        provenance,
        integrity,
        ai_stat,
        context,
        summary,
        evidences
    ) = engine.run(
        c2pa_data=c2pa,
        metadata_data=metadata,
        hash_data={},
        ai_data=ai,
        web_matches=[],
        fact_checks=[],
        claim=None
    )

    assert provenance == ProvenanceStatus.VERIFIED
    assert integrity == IntegrityStatus.CLEAR
    assert ai_stat == AIStatus.LOW
    assert context == ContextStatus.COHERENT
    assert conclusion == ConclusionLevel.NO_MAJOR_ALERT
    assert len(evidences) >= 3


def test_synthesis_engine_decontextualization_alert():
    engine = SynthesisEngine()
    
    metadata = {"make": None, "model": None}
    c2pa = {"has_manifest": False, "is_valid": False}
    ai = {"category": AIStatus.MODERATE, "raw_score": 0.55}
    
    web_matches = [
        WebMatchResult(
            url="https://example.com/mali-2024",
            domain="example.com",
            title="Image de 2024",
            match_type=WebMatchType.SIMILAR,
            match_score=0.9,
            earliest_date_found=None,
        )
    ]
    fact_checks = [
        FactCheckResult(
            publisher_name="AfricaCheck",
            publisher_site="africacheck.org",
            claim_reviewed="Image tournée à Ouagadougou en 2026",
            rating="Faux",
            review_url="https://africacheck.org/debunk",
            review_date=None,
        )
    ]

    (
        conclusion,
        provenance,
        integrity,
        ai_stat,
        context,
        summary,
        evidences
    ) = engine.run(
        c2pa_data=c2pa,
        metadata_data=metadata,
        hash_data={},
        ai_data=ai,
        web_matches=web_matches,
        fact_checks=fact_checks,
        claim="Événement d'aujourd'hui"
    )

    assert provenance == ProvenanceStatus.UNKNOWN
    assert context == ContextStatus.POTENTIAL_DECONTEXTUALIZATION
    assert conclusion == ConclusionLevel.IMPORTANT_ATTENTION
    assert any(e["source_engine"] == "fact_check" for e in evidences)


def test_full_orchestration(db_session, sample_valid_jpeg):
    from apps.api.app.services.analysis_service import analysis_service
    from apps.api.app.services.upload_service import upload_service

    mime, sha256_h, phash_v, name, prev = upload_service.validate_and_process(
        sample_valid_jpeg, "photo.jpg"
    )
    analysis, token = analysis_service.create_analysis(
        db=db_session,
        file_bytes=sample_valid_jpeg,
        filename=name,
        mime_type=mime,
        sha256_hash=sha256_h,
        phash_val=phash_v,
        preview_bytes=prev,
        claim="Test manifestation Ouagadougou"
    )

    # Process orchestrator
    orchestrator.process(db_session, analysis.id)

    res = analysis_service.get_result(db_session, analysis.id)
    assert res.status.value == "completed"
    assert res.conclusion_level is not None
    assert res.provenance_status is not None
    assert res.integrity_status is not None
    assert res.ai_status is not None
    assert res.context_status is not None
    assert len(res.evidences) > 0
