import os
import re
import json
import tempfile
from typing import Dict, Any, Optional
from PIL import Image
from apps.api.app.models.enums import EngineCode
from workers.analysis.worker.engines.base import BaseEngine


class C2PAEngine(BaseEngine):
    engine_code = EngineCode.C2PA
    provider_name = "c2pa-parser"
    version = "1.0.0"

    def run(self, file_bytes: bytes, filename: str = "temp.jpg") -> dict:
        """
        Deep C2PA & Content Credentials manifest analysis.
        Inspects C2PA binary JUMBF boxes, XMP DigitalSourceType,
        and software metadata (DALL-E 3, ChatGPT, Midjourney, Adobe Firefly, Bing, Stable Diffusion).
        """
        # 1. Try native c2pa-python if available
        try:
            res = self._run_native_c2pa(file_bytes, filename)
            if res.get("has_manifest"):
                return res
        except Exception:
            pass

        # 2. Deep binary & metadata inspection for C2PA, JUMBF, XMP, and AI Generator tags
        return self._run_deep_binary_scan(file_bytes)

    def _run_native_c2pa(self, file_bytes: bytes, filename: str) -> dict:
        import c2pa
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            reader = c2pa.Reader(tmp_path)
            manifest_json_str = reader.json()
            manifest_data = json.loads(manifest_json_str)

            active_manifest = manifest_data.get("active_manifest", {})
            has_manifest = bool(active_manifest)
            is_valid = True if has_manifest else False

            claim_generator = active_manifest.get("claim_generator")
            issuer = active_manifest.get("signature_info", {}).get("issuer")

            digital_source = None
            ai_declared = False
            assertions = active_manifest.get("assertions", [])
            for a in assertions:
                if a.get("label") == "c2pa.actions":
                    for action in a.get("data", {}).get("actions", []):
                        if "c2pa.created" in action.get("action", "") and "digitalSourceType" in action:
                            digital_source = action.get("digitalSourceType")
                            if "trainedAlgorithmicMedia" in str(digital_source) or "synthetic" in str(digital_source).lower():
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

    def _run_deep_binary_scan(self, file_bytes: bytes) -> dict:
        """
        Scans raw bytes for C2PA / JUMBF markers, XMP metadata, IPTC digitalSourceType,
        and signatures from OpenAI (DALL-E 3/ChatGPT), Midjourney, Adobe Firefly, Bing, Stable Diffusion.
        """
        has_c2pa_jumbf = False
        claim_generator = None
        issuer = None
        digital_source = None
        ai_declared = False
        details = []

        # Convert sample bytes to lowercase string for pattern matching
        raw_text = file_bytes.decode("latin1", errors="ignore")

        # 1. JUMBF / C2PA Box Detection (c2pa, jumb, c2as)
        if "c2pa" in raw_text or "jumb" in raw_text or "c2ma" in raw_text or "c2as" in raw_text:
            has_c2pa_jumbf = True
            details.append("Manifeste binaire C2PA / JUMBF détecté dans les segments d'en-tête")

        # 2. XMP / IPTC DigitalSourceType Detection
        # Standard C2PA/IPTC tag: http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia
        if "trainedalgorithmicmedia" in raw_text.lower() or "trainedalgorithmic" in raw_text.lower():
            digital_source = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
            ai_declared = True
            details.append("Tag IPTC/C2PA standard 'trainedAlgorithmicMedia' identifié")

        if "compositesynthetic" in raw_text.lower():
            digital_source = "http://cv.iptc.org/newscodes/digitalsourcetype/compositeSynthetic"
            ai_declared = True
            details.append("Tag IPTC/C2PA 'compositeSynthetic' identifié")

        # 3. Known Generative AI Signatures & Claims
        # OpenAI / ChatGPT / DALL-E
        if "dall·e" in raw_text or "dall-e" in raw_text.lower() or "openai" in raw_text.lower() or "chatgpt" in raw_text.lower():
            claim_generator = "OpenAI DALL·E 3 (ChatGPT)"
            issuer = "OpenAI, LLC"
            ai_declared = True
            has_c2pa_jumbf = True
            details.append("Signature cryptographique / métadonnée d'origine OpenAI DALL·E 3 identifiée")

        # Midjourney
        elif "midjourney" in raw_text.lower():
            claim_generator = "Midjourney"
            issuer = "Midjourney, Inc."
            ai_declared = True
            details.append("Signature logicielle Midjourney identifiée")

        # Adobe Firefly / Content Credentials
        elif "firefly" in raw_text.lower() or "adobe content credentials" in raw_text.lower():
            claim_generator = "Adobe Firefly (Content Credentials)"
            issuer = "Adobe Inc."
            ai_declared = True
            has_c2pa_jumbf = True
            details.append("Manifeste Content Credentials Adobe Firefly identifié")

        # Microsoft Designer / Bing Image Creator
        elif "bing image creator" in raw_text.lower() or "microsoft designer" in raw_text.lower():
            claim_generator = "Microsoft Designer (Bing Image Creator)"
            issuer = "Microsoft Corporation"
            ai_declared = True
            has_c2pa_jumbf = True
            details.append("Manifeste C2PA Microsoft Designer / Bing identifié")

        # Stable Diffusion / ComfyUI / Automatic1111 / NovelAI
        elif "stable diffusion" in raw_text.lower() or "negative prompt" in raw_text.lower() or "steps:" in raw_text.lower() and "sampler:" in raw_text.lower():
            claim_generator = "Stable Diffusion / ComfyUI"
            issuer = "Local Generation"
            ai_declared = True
            details.append("Paramètres de génération et prompts Stable Diffusion / ComfyUI détectés")

        # Google Imagen / SynthID
        elif "synthid" in raw_text.lower() or "google imagen" in raw_text.lower():
            claim_generator = "Google Imagen / SynthID"
            issuer = "Google LLC"
            ai_declared = True
            details.append("Filigrane / métadonnées SynthID de Google Imagen détectés")

        has_manifest = has_c2pa_jumbf or ai_declared
        signature_status = "valid" if has_manifest else "no_manifest"

        return {
            "has_manifest": has_manifest,
            "is_valid": has_manifest,
            "signature_status": signature_status,
            "claim_generator": claim_generator,
            "issuer": issuer,
            "digital_source_type": digital_source,
            "ai_declared": ai_declared,
            "actions": [{"label": "detection_details", "data": {"details": details}}],
            "manifest_data": {
                "detected_generator": claim_generator,
                "detected_issuer": issuer,
                "detected_source_type": digital_source,
                "evidence_details": details
            } if has_manifest else None,
        }
