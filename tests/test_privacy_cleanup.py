import pytest
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.cleanup_service import cleanup_service
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.enums import StoredObjectType
from sqlalchemy import select


def test_privacy_cleanup_removes_original_media(db_session, sample_valid_jpeg):
    mime, sha, phash, name, prev = upload_service.validate_and_process(
        sample_valid_jpeg, "image_to_clean.jpg"
    )
    analysis, token = analysis_service.create_analysis(
        db=db_session,
        file_bytes=sample_valid_jpeg,
        filename=name,
        mime_type=mime,
        sha256_hash=sha,
        phash_val=phash,
        preview_bytes=prev,
    )

    # Initial check: stored_objects exist and deleted_at is None
    orig_objs = db_session.execute(
        select(StoredObject).where(
            StoredObject.analysis_id == analysis.id,
            StoredObject.deleted_at.is_(None)
        )
    ).scalars().all()
    assert len(orig_objs) >= 2

    # Run cleanup
    cleanup_service.cleanup_original_media(db_session, analysis.id)

    # Verify original and preview objects are marked deleted
    active_objs = db_session.execute(
        select(StoredObject).where(
            StoredObject.analysis_id == analysis.id,
            StoredObject.deleted_at.is_(None)
        )
    ).scalars().all()
    assert len(active_objs) == 0
