from typing import Optional, List
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine
from workers.analysis.worker.adapters.base import WebContextProvider, WebMatchResult
from workers.analysis.worker.adapters.google_vision_adapter import GoogleVisionWebAdapter


class WebEngine(BaseEngine):
    engine_code = EngineCode.WEB_CONTEXT
    provider_name = "google_vision"
    version = "v1"

    def __init__(self, provider: Optional[WebContextProvider] = None):
        self.provider = provider or GoogleVisionWebAdapter()

    def run(
        self,
        file_bytes: bytes,
        phash: Optional[str] = None,
        claim: Optional[str] = None
    ) -> List[WebMatchResult]:
        return self.provider.search(file_bytes, phash=phash, claim=claim)
