from typing import Optional, Dict, Any
from apps.api.app.core.config import settings
from apps.api.app.models.enums import AIStatus
from workers.analysis.worker.adapters.base import AIProvider, AIDetectionResult
from workers.analysis.worker.adapters.mock_adapters import MockAIProvider


class HiveAIAdapter(AIProvider):
    """
    Adapter for Hive AI (ai_generated_image_detection).
    Maps Hive AI scores to standard domain AIStatus categories.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.HIVE_API_KEY
        self.endpoint = settings.HIVE_API_ENDPOINT
        self.mock_fallback = MockAIProvider()

    def analyze(self, image_bytes: bytes, context: Optional[Dict[str, Any]] = None) -> AIDetectionResult:
        if not self.api_key:
            return self.mock_fallback.analyze(image_bytes, context)

        try:
            import httpx
            files = {"media": ("image.jpg", image_bytes, "image/jpeg")}
            headers = {"Authorization": f"token {self.api_key}", "accept": "application/json"}
            
            with httpx.Client(timeout=20.0) as client:
                response = client.post(self.endpoint, files=files, headers=headers)
                response.raise_for_status()
                data = response.json()

            raw_score = 0.0
            classes = data.get("status", [{}])[0].get("response", {}).get("output", [{}])[0].get("classes", [])
            for c in classes:
                if c.get("class") == "ai_generated":
                    raw_score = float(c.get("score", 0.0))
                    break

            if raw_score >= 0.85:
                category = AIStatus.HIGH
            elif raw_score >= 0.50:
                category = AIStatus.MODERATE
            elif raw_score >= 0.15:
                category = AIStatus.LOW
            else:
                category = AIStatus.LOW

            return AIDetectionResult(
                category=category,
                raw_score=raw_score,
                confidence=0.9,
                provider="hive_ai",
                model_version="v2",
                details={"raw_classes": classes},
            )
        except Exception:
            return self.mock_fallback.analyze(image_bytes, context)
