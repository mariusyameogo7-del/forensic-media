from apps.api.app.core.config import settings

try:
    from celery import Celery

    celery_app = Celery(
        "forensic_media_worker",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=["workers.analysis.worker.tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_prefetch_multiplier=1,
    )
except ImportError:
    class DummyCelery:
        def task(self, *args, **kwargs):
            is_bound = kwargs.get("bind", False)
            def decorator(f):
                if is_bound:
                    f.delay = lambda *a, **k: f(None, *a, **k)
                else:
                    f.delay = lambda *a, **k: f(*a, **k)
                return f
            return decorator

    celery_app = DummyCelery()
