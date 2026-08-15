from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from apps.api.app.models.enums import AIStatus, WebMatchType


@dataclass
class AIDetectionResult:
    category: AIStatus
    raw_score: Optional[float]
    confidence: Optional[float]
    provider: str
    model_version: Optional[str]
    details: Optional[Dict[str, Any]] = None


@dataclass
class WebMatchResult:
    url: str
    domain: Optional[str]
    title: Optional[str]
    match_type: WebMatchType
    match_score: Optional[float]
    earliest_date_found: Optional[datetime]
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass
class FactCheckResult:
    publisher_name: str
    publisher_site: Optional[str]
    claim_reviewed: str
    rating: str
    review_url: str
    review_date: Optional[datetime]
    language: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class AIProvider(ABC):
    """Abstract interface for AI image generation and tampering estimation providers."""

    @abstractmethod
    def analyze(self, image_bytes: bytes, context: Optional[Dict[str, Any]] = None) -> AIDetectionResult:
        pass


class WebContextProvider(ABC):
    """Abstract interface for Web context and reverse image matching providers."""

    @abstractmethod
    def search(
        self,
        image_bytes: bytes,
        phash: Optional[str] = None,
        claim: Optional[str] = None
    ) -> List[WebMatchResult]:
        pass


class FactCheckProvider(ABC):
    """Abstract interface for Fact Check databases and Google Fact Check Tools API."""

    @abstractmethod
    def search(
        self,
        claim: Optional[str],
        web_matches: Optional[List[WebMatchResult]] = None
    ) -> List[FactCheckResult]:
        pass
