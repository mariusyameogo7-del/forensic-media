from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from apps.api.app.models.enums import AIStatus, WebMatchType
from workers.analysis.worker.adapters.base import (
    AIProvider,
    WebContextProvider,
    FactCheckProvider,
    AIDetectionResult,
    WebMatchResult,
    FactCheckResult,
)


class MockAIProvider(AIProvider):
    """Deterministic mock for AI generation estimation."""

    def __init__(self, default_status: AIStatus = AIStatus.LOW):
        self.default_status = default_status

    def analyze(self, image_bytes: bytes, context: Optional[Dict[str, Any]] = None) -> AIDetectionResult:
        # If image size is very small or specific pattern, return deterministic mock
        return AIDetectionResult(
            category=self.default_status,
            raw_score=0.12,
            confidence=0.88,
            provider="mock_hive_ai",
            model_version="2.0.0-mock",
            details={"artifacts_detected": False, "texture_score": 0.12},
        )


class MockWebContextProvider(WebContextProvider):
    """Deterministic mock for Web context searches."""

    def search(
        self,
        image_bytes: bytes,
        phash: Optional[str] = None,
        claim: Optional[str] = None
    ) -> List[WebMatchResult]:
        if claim and "ouagadougou" in claim.lower():
            # Simulate finding an older occurrence in Mali from 2024
            return [
                WebMatchResult(
                    url="https://afriquemedia.example.org/article/2024/05/manifestation-bamako",
                    domain="afriquemedia.example.org",
                    title="Manifestation populaire à Bamako en mai 2024",
                    match_type=WebMatchType.SIMILAR,
                    match_score=0.94,
                    earliest_date_found=datetime(2024, 5, 12, 10, 30, tzinfo=timezone.utc),
                    raw_payload={"source": "mock_google_vision"},
                )
            ]
        return []


class MockFactCheckProvider(FactCheckProvider):
    """Deterministic mock for Fact check lookups."""

    def search(
        self,
        claim: Optional[str],
        web_matches: Optional[List[WebMatchResult]] = None
    ) -> List[FactCheckResult]:
        if claim and ("ouagadougou" in claim.lower() or "manifestation" in claim.lower()):
            return [
                FactCheckResult(
                    publisher_name="FasoCheck",
                    publisher_site="fasocheck.org",
                    claim_reviewed="Cette vidéo/photo montre une mobilisation récente à Ouagadougou",
                    rating="Faux / Décontextualisé",
                    review_url="https://fasocheck.org/verification-image-mali-burkina",
                    review_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
                    language="fr",
                    raw_payload={"mock": True},
                )
            ]
        return []
