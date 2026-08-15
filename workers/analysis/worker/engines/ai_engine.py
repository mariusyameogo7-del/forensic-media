from typing import Optional
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine
from workers.analysis.worker.adapters.base import AIProvider
from workers.analysis.worker.adapters.hive_ai_adapter import HiveAIAdapter


class AIEngine(BaseEngine):
    engine_code = EngineCode.AI
    provider_name = "hive_ai"
    version = "v2"

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or HiveAIAdapter()

    def run(self, file_bytes: bytes) -> dict:
        detection = self.provider.analyze(file_bytes)
        return {
            "provider": detection.provider,
            "model_version": detection.model_version,
            "raw_score": detection.raw_score,
            "category": detection.category,
            "confidence": detection.confidence,
            "details": detection.details,
        }
