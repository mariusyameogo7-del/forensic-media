import pytest
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.report_service import report_service
from workers.analysis.worker.orchestrator import orchestrator


def test_report_immutability_and_versioning(db_session, sample_valid_jpeg):
    mime, sha, phash, name, prev = upload_service.validate_and_process(
        sample_valid_jpeg, "image_report.jpg"
    )
    analysis, token = analysis_service.create_analysis(
        db=db_session,
        file_bytes=sample_valid_jpeg,
        filename=name,
        mime_type=mime,
        sha256_hash=sha,
        phash_val=phash,
        preview_bytes=prev,
        claim="Analyse pour test rapport"
    )
    orchestrator.process(db_session, analysis.id)

    # 1. Generate Report v1
    report1 = report_service.create_report(db_session, analysis)
    assert report1.report_version == 1
    assert report1.pdf_sha256 is not None
    assert len(report1.pdf_sha256) == 64
    assert report1.snapshot_data["analysis"]["public_id"] == analysis.public_id

    # 2. Generate Report v2 (creates distinct version without mutating v1)
    report2 = report_service.create_report(db_session, analysis)
    assert report2.report_version == 2
    assert report2.id != report1.id
    assert report1.report_version == 1
