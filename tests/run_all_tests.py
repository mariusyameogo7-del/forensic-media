import unittest
import io
import sys
from uuid import UUID
from datetime import datetime, timezone
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure python path includes workspace
sys.path.insert(0, ".")

from apps.api.app.core.database import Base
from apps.api.app.models.enums import (
    AccountType,
    AnalysisStatus,
    ConclusionLevel,
    ProvenanceStatus,
    IntegrityStatus,
    AIStatus,
    ContextStatus,
    StoredObjectType,
    EvidenceType,
    EvidenceSeverity,
    WebMatchType,
)
from apps.api.app.models import (
    User,
    UserPreferences,
    Analysis,
    AnalysisAccessToken,
    StoredObject,
    AnalysisEngineRun,
    C2PAResult,
    MetadataResult,
    AIResult,
    WebMatch,
    FactCheckMatch,
    SynthesisResult,
    SynthesisEvidence,
    AnalysisReport,
    AnalysisEvent,
)
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.cleanup_service import cleanup_service
from apps.api.app.services.report_service import report_service
from apps.api.app.core.errors import FileSizeExceededError, UnsupportedMediaTypeError, InvalidFileError
from apps.api.app.core.security import hash_token
from workers.analysis.worker.engines.synthesis_engine import SynthesisEngine
from workers.analysis.worker.adapters.base import WebMatchResult, FactCheckResult
from workers.analysis.worker.orchestrator import orchestrator


class ForensicMediaTestSuite(unittest.TestCase):
    def setUp(self):
        # Create fresh in-memory SQLite database
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.Session()

        # Create valid sample image bytes
        img = Image.new("RGB", (200, 200), color=(60, 120, 216))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        self.sample_jpeg = buf.getvalue()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    # 1. TEST UPLOAD VALIDATION
    def test_upload_jpeg_valid(self):
        mime, sha256_val, phash_val, norm_name, preview = upload_service.validate_and_process(
            file_bytes=self.sample_jpeg,
            filename="photo_test.jpg",
            content_type="image/jpeg"
        )
        self.assertEqual(mime, "image/jpeg")
        self.assertEqual(len(sha256_val), 64)
        self.assertIsNotNone(phash_val)
        self.assertTrue(len(preview) > 0)

    def test_upload_size_limit_exceeded(self):
        huge_bytes = b"\xFF\xD8\xFF" + b"\x00" * (21 * 1024 * 1024)
        with self.assertRaises(FileSizeExceededError):
            upload_service.validate_and_process(
                file_bytes=huge_bytes,
                filename="too_heavy.jpg",
                content_type="image/jpeg"
            )

    def test_upload_fake_extension(self):
        non_image = b"Random plain text content without image header"
        with self.assertRaises(UnsupportedMediaTypeError):
            upload_service.validate_and_process(
                file_bytes=non_image,
                filename="fake.jpg",
                content_type="image/jpeg"
            )

    # 2. TEST ANONYMOUS ACCESS & SECURITY
    def test_anonymous_analysis_creation_and_token_security(self):
        mime, sha, phash, name, prev = upload_service.validate_and_process(
            self.sample_jpeg, "image_anon.jpg"
        )
        analysis, plain_token = analysis_service.create_analysis(
            db=self.db,
            file_bytes=self.sample_jpeg,
            filename=name,
            mime_type=mime,
            sha256_hash=sha,
            phash_val=phash,
            preview_bytes=prev,
        )

        self.assertIsNone(analysis.user_id)
        self.assertIsNotNone(plain_token)
        self.assertTrue(analysis.public_id.startswith("AN-"))

        # Verify access with valid plain token
        self.assertTrue(analysis_service.verify_access(self.db, analysis, user=None, raw_token=plain_token))

        # Verify access fails with invalid token
        from apps.api.app.core.errors import UnauthorizedError
        with self.assertRaises(UnauthorizedError):
            analysis_service.verify_access(self.db, analysis, user=None, raw_token="wrong_token_xyz")

    # 3. TEST SYNTHESIS ENGINE
    def test_synthesis_engine_prudent_rules(self):
        engine = SynthesisEngine()
        
        # Test Case: C2PA valid + metadata -> No major alert
        conclusion, prov, integ, ai, ctx, summary, evs = engine.run(
            c2pa_data={"has_manifest": True, "is_valid": True, "claim_generator": "Photoshop"},
            metadata_data={"make": "Nikon", "model": "D850"},
            hash_data={},
            ai_data={"category": AIStatus.LOW, "raw_score": 0.04},
            web_matches=[],
            fact_checks=[],
            claim=None
        )
        self.assertEqual(prov, ProvenanceStatus.VERIFIED)
        self.assertEqual(integ, IntegrityStatus.CLEAR)
        self.assertEqual(ai, AIStatus.LOW)
        self.assertEqual(ctx, ContextStatus.COHERENT)
        self.assertEqual(conclusion, ConclusionLevel.NO_MAJOR_ALERT)
        self.assertTrue(len(evs) >= 3)

        # Test Case: Fact-check exists -> Decontextualization Alert
        fc = FactCheckResult(
            publisher_name="AfricaCheck",
            publisher_site="africacheck.org",
            claim_reviewed="Manifestation récente",
            rating="Faux",
            review_url="https://africacheck.org",
            review_date=None
        )
        conclusion2, prov2, integ2, ai2, ctx2, summary2, evs2 = engine.run(
            c2pa_data=None,
            metadata_data=None,
            hash_data={},
            ai_data={"category": AIStatus.MODERATE, "raw_score": 0.45},
            web_matches=[],
            fact_checks=[fc],
            claim="Photo d'hier"
        )
        self.assertEqual(ctx2, ContextStatus.POTENTIAL_DECONTEXTUALIZATION)
        self.assertEqual(conclusion2, ConclusionLevel.IMPORTANT_ATTENTION)

    # 4. TEST ORCHESTRATION & PERSISTENCE OF 15 ENTITIES
    def test_full_pipeline_orchestration(self):
        mime, sha, phash, name, prev = upload_service.validate_and_process(
            self.sample_jpeg, "test_pipeline.jpg"
        )
        analysis, token = analysis_service.create_analysis(
            db=self.db,
            file_bytes=self.sample_jpeg,
            filename=name,
            mime_type=mime,
            sha256_hash=sha,
            phash_val=phash,
            preview_bytes=prev,
            claim="Manifestation à Ouagadougou"
        )

        # Execute orchestrator
        orchestrator.process(self.db, analysis.id)

        self.assertEqual(analysis.status, AnalysisStatus.COMPLETED)
        self.assertIsNotNone(analysis.conclusion_level)
        self.assertIsNotNone(analysis.provenance_status)
        self.assertIsNotNone(analysis.integrity_status)
        self.assertIsNotNone(analysis.ai_status)
        self.assertIsNotNone(analysis.context_status)
        self.assertTrue(len(analysis.synthesis_evidences) > 0)
        self.assertTrue(len(analysis.engine_runs) == 7)

    # 5. TEST REPORT IMMUTABILITY & VERSIONING
    def test_immutable_report_generation(self):
        mime, sha, phash, name, prev = upload_service.validate_and_process(
            self.sample_jpeg, "test_report.jpg"
        )
        analysis, token = analysis_service.create_analysis(
            db=self.db,
            file_bytes=self.sample_jpeg,
            filename=name,
            mime_type=mime,
            sha256_hash=sha,
            phash_val=phash,
            preview_bytes=prev,
        )
        orchestrator.process(self.db, analysis.id)

        # Create Report v1
        rep1 = report_service.create_report(self.db, analysis)
        self.assertEqual(rep1.report_version, 1)
        self.assertEqual(len(rep1.pdf_sha256), 64)
        self.assertEqual(rep1.snapshot_data["analysis"]["public_id"], analysis.public_id)

        # Create Report v2
        rep2 = report_service.create_report(self.db, analysis)
        self.assertEqual(rep2.report_version, 2)
        self.assertEqual(rep1.report_version, 1) # Immutability preserved

    # 6. TEST PRIVACY MEDIA CLEANUP
    def test_privacy_cleanup(self):
        mime, sha, phash, name, prev = upload_service.validate_and_process(
            self.sample_jpeg, "privacy_test.jpg"
        )
        analysis, token = analysis_service.create_analysis(
            db=self.db,
            file_bytes=self.sample_jpeg,
            filename=name,
            mime_type=mime,
            sha256_hash=sha,
            phash_val=phash,
            preview_bytes=prev,
        )
        cleanup_service.cleanup_original_media(self.db, analysis.id)

        from sqlalchemy import select
        active_objs = self.db.execute(
            select(StoredObject).where(
                StoredObject.analysis_id == analysis.id,
                StoredObject.deleted_at.is_(None)
            )
        ).scalars().all()
        self.assertEqual(len(active_objs), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
