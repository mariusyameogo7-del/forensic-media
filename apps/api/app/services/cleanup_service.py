from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from apps.api.app.models.enums import StoredObjectType
from apps.api.app.models.analysis import Analysis
from apps.api.app.models.stored_object import StoredObject
from apps.api.app.models.event import AnalysisEvent
from apps.api.app.services.storage_service import storage_service


class CleanupService:
    """
    Implements the privacy-first data lifecycle:
    Removes original files and thumbnails/derivatives when retention policy dictates it.
    """

    def cleanup_original_media(self, db: Session, analysis_id) -> bool:
        """
        Deletes the original media file and preview thumbnails for an analysis.
        Leaves the analysis result metadata and reports intact.
        """
        stored_objects = db.execute(
            select(StoredObject).where(
                StoredObject.analysis_id == analysis_id,
                StoredObject.object_type.in_([StoredObjectType.ORIGINAL, StoredObjectType.PREVIEW, StoredObjectType.THUMBNAIL]),
                StoredObject.deleted_at.is_(None)
            )
        ).scalars().all()

        for obj in stored_objects:
            storage_service.delete_file(obj.bucket_name, obj.storage_path)
            obj.deleted_at = datetime.now(timezone.utc)

        # Log event
        event = AnalysisEvent(
            analysis_id=analysis_id,
            event_type="media_deleted",
            message="Fichier média original et aperçus supprimés conformément à la politique de confidentialité.",
            metadata_json={"deleted_objects_count": len(stored_objects)}
        )
        db.add(event)
        db.commit()
        return True


cleanup_service = CleanupService()
