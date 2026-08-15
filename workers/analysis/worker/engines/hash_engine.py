import io
from PIL import Image
from apps.api.app.core.security import compute_sha256
from apps.api.app.models.enums import EngineCode
from apps.api.app.services.upload_service import compute_perceptual_hash
from workers.analysis.worker.engines.base import BaseEngine


class HashEngine(BaseEngine):
    engine_code = EngineCode.HASHES
    provider_name = "internal_hashlib"
    version = "1.0.0"

    def run(self, file_bytes: bytes) -> dict:
        sha256_val = compute_sha256(file_bytes)
        
        with Image.open(io.BytesIO(file_bytes)) as img:
            rgb_img = img.convert("RGB") if img.mode not in ("RGB", "L") else img
            phash_val = compute_perceptual_hash(rgb_img)

        return {
            "sha256": sha256_val,
            "phash": phash_val,
        }
