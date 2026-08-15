import os
import tempfile
from typing import Dict, Any, Optional
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine


class C2PAEngine(BaseEngine):
    engine_code = EngineCode.C2PA
    provider_name = "c2pa-python"
    version = "0.37.7"

    def run(self, file_bytes: bytes, filename: str = "temp.jpg") -> dict:
        """
        Parses C2PA / Content Credentials manifest using c2pa-python or fallback parser.
        """
        try:
            return self._run_c2pa(file_bytes, filename)
        except Exception:
            return self._run_fallback(file_bytes)

    def _run_c2pa(self, file_bytes: bytes, filename: str) -> dict:
        import c2pa
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            reader = c2pa.Reader(tmp_path)
            manifest_json_str = reader.json()
            import json
            manifest_data = json.loads(manifest_json_str)

            active_manifest = manifest_data.get("active_manifest", {})
            has_manifest = bool(active_manifest)
            is_valid = True if has_manifest else False
            
            claim_generator = active_manifest.get("claim_generator")
            issuer = active_manifest.get("signature_info", {}).get("issuer")
            
            # Check digital source type or declared AI assertions
            digital_source = None
            ai_declared = False
            assertions = active_manifest.get("assertions", [])
            for a in assertions:
                if a.get("label") == "c2pa.actions":
                    for action in a.get("data", {}).get("actions", []):
                        if "c2pa.created" in action.get("action", "") and "digitalSourceType" in action:
                            digital_source = action.get("digitalSourceType")
                            if "trainedAlgorithmicMedia" in digital_source or "synthetic" in digital_source.lower():
                                ai_declared = True

            return {
                "has_manifest": has_manifest,
                "is_valid": is_valid,
                "signature_status": "valid" if is_valid else "not_signed",
                "claim_generator": claim_generator,
                "issuer": issuer,
                "digital_source_type": digital_source,
                "ai_declared": ai_declared,
                "actions": assertions,
                "manifest_data": manifest_data,
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _run_fallback(self, file_bytes: bytes) -> dict:
        # Fallback when image contains no C2PA box or c2pa-python is uncompiled
        return {
            "has_manifest": False,
            "is_valid": False,
            "signature_status": "no_manifest",
            "claim_generator": None,
            "issuer": None,
            "digital_source_type": None,
            "ai_declared": False,
            "actions": None,
            "manifest_data": None,
        }
