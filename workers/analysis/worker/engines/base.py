import time
from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional
from datetime import datetime, timezone
from apps.api.app.models.enums import EngineCode, EngineRunStatus
from apps.api.app.models.engine_run import AnalysisEngineRun


class BaseEngine(ABC):
    """Base class for all analysis engines handling execution timing and status transitions."""

    engine_code: EngineCode
    provider_name: str
    version: str = "1.0.0"

    def execute_run(self, engine_run: AnalysisEngineRun, *args, **kwargs) -> Tuple[EngineRunStatus, Optional[Any], Optional[str]]:
        """
        Executes engine logic with execution metrics tracking.
        Returns:
            (status, result_payload, error_message)
        """
        start_time = time.time()
        engine_run.status = EngineRunStatus.RUNNING
        engine_run.started_at = datetime.now(timezone.utc)

        try:
            result = self.run(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            engine_run.status = EngineRunStatus.COMPLETED
            engine_run.completed_at = datetime.now(timezone.utc)
            engine_run.duration_ms = duration_ms
            return EngineRunStatus.COMPLETED, result, None
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            engine_run.status = EngineRunStatus.FAILED
            engine_run.completed_at = datetime.now(timezone.utc)
            engine_run.duration_ms = duration_ms
            engine_run.error_code = f"ERR_{self.engine_code.value.upper()}"
            engine_run.public_error_message = f"Le moteur {self.engine_code.value} a rencontré une erreur d'exécution."
            engine_run.private_error_details = {"exception": str(e)}
            return EngineRunStatus.FAILED, None, str(e)

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        pass
