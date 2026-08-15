from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppError(Exception):
    """Base application exception with stable machine error codes."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidFileError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="INVALID_FILE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class FileSizeExceededError(AppError):
    def __init__(self, max_size_mb: int = 20):
        super().__init__(
            code="FILE_SIZE_EXCEEDED",
            message=f"La taille du fichier dépasse la limite maximale autorisée ({max_size_mb} MiB).",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


class UnsupportedMediaTypeError(AppError):
    def __init__(self, message: str = "Format d'image non supporté. Formats acceptés : JPG, JPEG, PNG, WEBP."):
        super().__init__(
            code="UNSUPPORTED_MEDIA_TYPE",
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} introuvable pour l'identifiant '{identifier}'.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Accès non autorisé. Token d'accès manquant ou invalide."):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Accès refusé. Vous n'avez pas les droits sur cette ressource."):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class AnalysisFailedError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="ANALYSIS_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
