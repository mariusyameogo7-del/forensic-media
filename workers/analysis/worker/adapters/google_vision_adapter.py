from typing import Optional, List
from urllib.parse import urlparse
from datetime import datetime, timezone
from apps.api.app.core.config import settings
from apps.api.app.models.enums import WebMatchType
from workers.analysis.worker.adapters.base import WebContextProvider, WebMatchResult
from workers.analysis.worker.adapters.mock_adapters import MockWebContextProvider


class GoogleVisionWebAdapter(WebContextProvider):
    """
    Adapter for Google Cloud Vision Web Detection API.
    Identifies exact and visually similar matches found across the web.
    """

    def __init__(self):
        self.mock_fallback = MockWebContextProvider()

    def search(
        self,
        image_bytes: bytes,
        phash: Optional[str] = None,
        claim: Optional[str] = None
    ) -> List[WebMatchResult]:
        if not settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
            return self.mock_fallback.search(image_bytes, phash, claim)

        try:
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_bytes)
            response = client.web_detection(image=image)
            web_detection = response.web_detection

            results = []
            if web_detection.pages_with_matching_images:
                for page in web_detection.pages_with_matching_images[:10]:
                    domain = urlparse(page.url).netloc
                    results.append(
                        WebMatchResult(
                            url=page.url,
                            domain=domain,
                            title=page.page_title or "Page Web correspondante",
                            match_type=WebMatchType.EXACT if page.full_matching_images else WebMatchType.SIMILAR,
                            match_score=0.95 if page.full_matching_images else 0.80,
                            earliest_date_found=None,
                            raw_payload={"page_title": page.page_title},
                        )
                    )
            return results
        except Exception:
            return self.mock_fallback.search(image_bytes, phash, claim)
