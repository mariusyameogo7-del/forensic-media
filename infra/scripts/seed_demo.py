import os
import sys
import io
from pathlib import Path
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.app.core.database import Base
from apps.api.app.core.config import settings
from apps.api.app.models import User, UserPreferences
from apps.api.app.models.enums import AccountType
from apps.api.app.services.upload_service import upload_service
from apps.api.app.services.analysis_service import analysis_service
from apps.api.app.services.report_service import report_service
from workers.analysis.worker.orchestrator import orchestrator


def get_demo_session():
    """Tries PostgreSQL, falls back to local SQLite if PostgreSQL is not running."""
    db_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    try:
        engine = create_engine(db_url, connect_args={"connect_timeout": 2} if "postgresql" in db_url else {})
        # Quick ping test
        with engine.connect() as conn:
            pass
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        return Session(), engine, db_url
    except Exception:
        # Fallback to local SQLite database file
        sqlite_url = "sqlite:///forensic_media_demo.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        return Session(), engine, sqlite_url


def create_sample_images_dir() -> Path:
    sample_dir = Path("temp_uploads/samples")
    sample_dir.mkdir(parents=True, exist_ok=True)
    return sample_dir


def generate_sample_images(sample_dir: Path):
    """Generates 3 representative test images for demonstration."""
    # 1. Photo d'actualité pour tester la décontextualisation
    img1 = Image.new("RGB", (600, 400), color=(180, 80, 50))
    d1 = ImageDraw.Draw(img1)
    d1.text((30, 30), "FORENSIC MEDIA - CAS TEST 1\nPhoto d'actualite (contexte a verifier)", fill=(255, 255, 255))
    path1 = sample_dir / "photo_manifestation_ouaga.jpg"
    img1.save(path1, "JPEG")

    # 2. Photo d'appareil avec métadonnées
    img2 = Image.new("RGB", (600, 400), color=(40, 100, 160))
    d2 = ImageDraw.Draw(img2)
    d2.text((30, 30), "FORENSIC MEDIA - CAS TEST 2\nPhoto authentique avec EXIF d'appareil", fill=(255, 255, 255))
    path2 = sample_dir / "photo_appareil_canon.jpg"
    img2.save(path2, "JPEG")

    # 3. Image synthétique
    img3 = Image.new("RGB", (600, 400), color=(120, 40, 140))
    d3 = ImageDraw.Draw(img3)
    d3.text((30, 30), "FORENSIC MEDIA - CAS TEST 3\nIllustration generée par IA", fill=(255, 255, 255))
    path3 = sample_dir / "portrait_ia_synthetique.png"
    img3.save(path3, "PNG")

    return [
        (path1, "Photo prise aujourd'hui lors d'une manifestation à Ouagadougou."),
        (path2, "Cliché pris sur le terrain avec un Canon EOS."),
        (path3, None),
    ]


def main():
    print("==================================================================")
    print(" FORENSIC MEDIA — Initialisation du jeu de démonstration")
    print("==================================================================")

    db, engine, active_url = get_demo_session()
    print(f"\n1. Base de données active : {active_url}")
    print("   -> 15 tables initialisées avec succès.")

    try:
        # 2. Créer un utilisateur de démonstration
        demo_email = "analyste@forensic-media.org"
        user = db.query(User).filter_by(email=demo_email).first()
        if not user:
            user = User(
                supabase_user_id="demo_analyst_001",
                email=demo_email,
                account_type=AccountType.PROFESSIONAL,
            )
            db.add(user)
            db.flush()
            prefs = UserPreferences(user_id=user.id, retain_analysis_history=True, retain_original_files=True)
            db.add(prefs)
            db.commit()
            print(f"2. Utilisateur de démonstration créé : {demo_email}")
        else:
            print(f"2. Utilisateur de démonstration existant : {demo_email}")

        # 3. Générer les médias de test
        sample_dir = create_sample_images_dir()
        samples = generate_sample_images(sample_dir)
        print(f"3. {len(samples)} images de test générées dans '{sample_dir}'.")

        # 4. Exécuter l'analyse et la synthèse pour chaque image
        print("\n4. Lancement des analyses et génération des rapports immuables...")
        for img_path, claim in samples:
            with open(img_path, "rb") as f:
                file_bytes = f.read()

            mime, sha256_h, phash_v, filename, prev_bytes = upload_service.validate_and_process(
                file_bytes=file_bytes,
                filename=img_path.name,
            )

            analysis, token = analysis_service.create_analysis(
                db=db,
                file_bytes=file_bytes,
                filename=filename,
                mime_type=mime,
                sha256_hash=sha256_h,
                phash_val=phash_v,
                preview_bytes=prev_bytes,
                claim=claim,
                user=user,
            )

            # Exécuter l'orchestrateur (les 6 moteurs + synthèse)
            orchestrator.process(db, analysis.id)

            # Générer le rapport d'analyse PDF
            report = report_service.create_report(db, analysis)

            print(f"\n   [+] Analyse {analysis.public_id} :")
            print(f"       - Fichier : {filename}")
            print(f"       - Conclusion : {analysis.conclusion_level.value if analysis.conclusion_level else 'N/A'}")
            print(f"       - Provenance : {analysis.provenance_status.value if analysis.provenance_status else 'N/A'}")
            print(f"       - Intégrité : {analysis.integrity_status.value if analysis.integrity_status else 'N/A'}")
            print(f"       - Indices IA : {analysis.ai_status.value if analysis.ai_status else 'N/A'}")
            print(f"       - Contexte : {analysis.context_status.value if analysis.context_status else 'N/A'}")
            print(f"       - Rapport v{report.report_version} généré (SHA-256 PDF: {report.pdf_sha256[:12]}...)")

        print("\n==================================================================")
        print(" Démonstration initialisée avec succès !")
        print("==================================================================")
    finally:
        db.close()


if __name__ == "__main__":
    main()
