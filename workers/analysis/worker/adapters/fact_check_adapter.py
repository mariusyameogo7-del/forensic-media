from typing import Optional, List
from datetime import datetime, timezone
from apps.api.app.core.config import settings
from workers.analysis.worker.adapters.base import FactCheckProvider, FactCheckResult, WebMatchResult
from workers.analysis.worker.adapters.mock_adapters import MockFactCheckProvider


class GoogleFactCheckAdapter(FactCheckProvider):
    """
    Adapter for Google Fact Check Tools API (factchecktools.googleapis.com).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_FACT_CHECK_API_KEY
        self.endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.mock_fallback = MockFactCheckProvider()

    def search(
        self,
        claim: Optional[str],
        web_matches: Optional[List[WebMatchResult]] = None
    ) -> List[FactCheckResult]:
        if not self.api_key or not claim:
            return self.mock_fallback.search(claim, web_matches)

        try:
            import httpx
            params = {
                "query": claim,
                "key": self.api_key,
                "languageCode": "fr",
                "pageSize": 10,
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.get(self.endpoint, params=params)
                res.raise_for_status()
                data = res.json()

            results = []
            claims_data = data.get("claims", [])
            for c in claims_data:
                reviews = c.get("claimReview", [])
                for r in reviews:
                    publisher = r.get("publisher", {})
                    results.append(
                        FactCheckResult(
                            publisher_name=publisher.get("name", "Fact-checker"),
                            publisher_site=publisher.get("site"),
                            claim_reviewed=c.get("text", claim),
                            rating=r.get("textualRating", "Non vérifié"),
                            review_url=r.get("url", ""),
                            review_date=None,
                            language=r.get("languageCode", "fr"),
                            raw_payload=r,
                        )
                    )
            return results if results else self.mock_fallback.search(claim, web_matches)
        except Exception:
            return self.mock_fallback.search(claim, web_matches)
