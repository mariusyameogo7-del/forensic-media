from uuid import UUID
from apps.api.app.core.database import SessionLocal
from workers.analysis.worker.celery_app import celery_app
from workers.analysis.worker.orchestrator import orchestrator


@celery_app.task(name="process_analysis_task", bind=True, max_retries=2)
def process_analysis_task(self, analysis_id_str: str):
    """
    Celery background task for media processing.
    Receives ONLY the analysis_id UUID string.
    Never passes binary media via the Redis broker.
    """
    db = SessionLocal()
    try:
        analysis_id = UUID(analysis_id_str)
        orchestrator.process(db=db, analysis_id=analysis_id)
        return {"status": "success", "analysis_id": analysis_id_str}
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=5)
    finally:
        db.close()
