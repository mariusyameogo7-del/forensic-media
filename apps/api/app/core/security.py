import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from apps.api.app.core.config import settings


def generate_anonymous_token() -> Tuple[str, str, datetime]:
    """
    Generates a secure random access token for anonymous analysis.
    Returns:
        token_secret (str): The plain token returned ONCE to the client.
        token_hash (str): The SHA-256 hex digest to be stored in the database.
        expires_at (datetime): The expiration timestamp (default 30 days).
    """
    token_secret = secrets.token_urlsafe(32)
    token_hash = hash_token(token_secret)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.ANONYMOUS_TOKEN_EXPIRY_DAYS)
    return token_secret, token_hash, expires_at


def hash_token(token: str) -> str:
    """Computes SHA-256 hex digest of a token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def compute_sha256(data: bytes) -> str:
    """Computes SHA-256 of raw binary data."""
    return hashlib.sha256(data).hexdigest()


def generate_public_id() -> str:
    """Generates a human-friendly public ID for display (e.g. AN-2026-A8B9C2)."""
    current_year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    return f"AN-{current_year}-{suffix}"
