from typing import Optional, List
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine
from workers.analysis.worker.adapters.base import FactCheckProvider, FactCheckResult, WebMatchResult
from workers.analysis.worker.adapters.fact_check_adapter import GoogleFactCheckAdapter


class FactCheckEngine(BaseEngine):
    engine_code = EngineCode.FACT_CHECK
    provider_name = "google_fact_check"
    version = "v1"

    def __init__(self, provider: Optional[FactCheckProvider] = None):
        self.provider = provider or GoogleFactCheckAdapter()

    def run(
        self,
        claim: Optional[str],
        web_matches: Optional[List[WebMatchResult]] = None
    ) -> List[FactCheckResult]:
        return self.provider.search(claim, web_matches)
