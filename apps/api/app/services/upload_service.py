import io
from typing import Tuple, Optional
from PIL import Image
from apps.api.app.core.config import settings
from apps.api.app.core.errors import FileSizeExceededError, UnsupportedMediaTypeError, InvalidFileError
from apps.api.app.core.security import compute_sha256

ALLOWED_MIME_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
}


def compute_perceptual_hash(img: Image.Image) -> str:
    """Computes a 64-bit difference perceptual hash (dHash) using Pillow."""
    try:
        import imagehash
        return str(imagehash.phash(img))
    except Exception:
        resized = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
        diff = []
        for row in range(8):
            for col in range(8):
                diff.append(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
        decimal_val = 0
        for bit in diff:
            decimal_val = (decimal_val << 1) | bit
        return f"{decimal_val:016x}"


class UploadService:
    """
    Validates uploaded images, enforces strict size limits, checks real binary signatures,
    and computes SHA-256 and pHash before any transformation.
    """

    def validate_and_process(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> Tuple[str, str, str, str, bytes]:
        # 1. Strict Size Check
        file_size = len(file_bytes)
        if file_size == 0:
            raise InvalidFileError("Le fichier envoyé est vide.")
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileSizeExceededError(max_size_mb=20)

        # 2. Magic Bytes / Signature Verification
        detected_mime = self._detect_mime_type(file_bytes)
        if not detected_mime or detected_mime not in ALLOWED_MIME_TYPES:
            raise UnsupportedMediaTypeError(
                f"Type de fichier non supporté. Les formats acceptés sont JPG, JPEG, PNG et WEBP."
            )

        # 3. True Image Decode Verification (Pillow)
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()
        except Exception as e:
            raise InvalidFileError(f"Le fichier est corrompu ou ne peut pas être décodé en tant qu'image valide : {str(e)}")

        # 4. SHA-256 Computed IMMEDIATELY on the Raw Original Bytes
        sha256_hash = compute_sha256(file_bytes)

        # 5. pHash & Preview Generation
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                rgb_img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
                phash_val = compute_perceptual_hash(rgb_img)

                # Generate a max 800px preview thumbnail
                preview_img = rgb_img.copy()
                preview_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                preview_io = io.BytesIO()
                preview_img.save(preview_io, format="JPEG", quality=85)
                preview_bytes = preview_io.getvalue()
        except Exception as e:
            raise InvalidFileError(f"Erreur lors du calcul de l'empreinte perceptuelle : {str(e)}")

        return detected_mime, sha256_hash, phash_val, filename, preview_bytes

    def _detect_mime_type(self, data: bytes) -> Optional[str]:
        """Detects MIME type from file header magic bytes."""
        if len(data) < 12:
            return None
        if data.startswith(b"\xFF\xD8\xFF"):
            return "image/jpeg"
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return "image/webp"
        return None


upload_service = UploadService()
