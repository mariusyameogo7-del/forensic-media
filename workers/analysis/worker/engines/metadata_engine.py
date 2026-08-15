import json
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime
from PIL import Image, ExifTags
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine


class MetadataEngine(BaseEngine):
    engine_code = EngineCode.METADATA
    provider_name = "exiftool"
    version = "13.59"

    def run(self, file_bytes: bytes, filename: str = "temp.jpg") -> dict:
        # Try running ExifTool binary
        try:
            return self._run_exiftool(file_bytes, filename)
        except Exception:
            # Fallback to Pillow EXIF parser
            return self._run_pillow(file_bytes)

    def _run_exiftool(self, file_bytes: bytes, filename: str) -> dict:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            cmd = ["exiftool", "-j", "-G", tmp_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                raw_list = json.loads(res.stdout)
                raw = raw_list[0] if raw_list else {}

                return {
                    "make": raw.get("EXIF:Make") or raw.get("Make"),
                    "model": raw.get("EXIF:Model") or raw.get("Model"),
                    "software": raw.get("EXIF:Software") or raw.get("Software"),
                    "original_date": None,
                    "modify_date": None,
                    "has_gps": "EXIF:GPSLatitude" in raw or "GPSLatitude" in raw,
                    "gps_latitude": float(raw.get("Composite:GPSLatitude", 0)) if "Composite:GPSLatitude" in raw else None,
                    "gps_longitude": float(raw.get("Composite:GPSLongitude", 0)) if "Composite:GPSLongitude" in raw else None,
                    "image_width": raw.get("File:ImageWidth") or raw.get("ImageWidth"),
                    "image_height": raw.get("File:ImageHeight") or raw.get("ImageHeight"),
                    "color_space": raw.get("EXIF:ColorSpace") or raw.get("ColorSpace"),
                    "raw_metadata": raw,
                }
            raise RuntimeError(res.stderr)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _run_pillow(self, file_bytes: bytes) -> dict:
        import io
        with Image.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
            raw_exif = {}
            make, model, software = None, None, None
            has_gps = False

            exif = img.getexif()
            if exif:
                for k, v in exif.items():
                    tag = ExifTags.TAGS.get(k, str(k))
                    raw_exif[tag] = str(v)
                    if tag == "Make":
                        make = str(v)
                    elif tag == "Model":
                        model = str(v)
                    elif tag == "Software":
                        software = str(v)
                    elif "GPS" in tag:
                        has_gps = True

            return {
                "make": make,
                "model": model,
                "software": software,
                "original_date": None,
                "modify_date": None,
                "has_gps": has_gps,
                "gps_latitude": None,
                "gps_longitude": None,
                "image_width": width,
                "image_height": height,
                "color_space": img.mode,
                "raw_metadata": raw_exif,
            }
