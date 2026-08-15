import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.app.core.config import settings
from apps.api.app.core.database import Base, engine


def check_database_connection():
    print("\n--- 1. Vérification de la connexion Base de Données PostgreSQL ---")
    try:
        with engine.connect() as conn:
            print(f"✅ Connexion réussie à la base de données : {engine.url.host or 'localhost'}")
            print("   Application du schéma et des 15 tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Les 15 tables ont été initialisées avec succès dans la base.")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")
        return False


def setup_supabase_buckets():
    print("\n--- 2. Configuration des 3 Buckets Privés dans Supabase Storage ---")
    supabase_url = settings.SUPABASE_URL.rstrip("/")
    service_key = settings.SUPABASE_SERVICE_ROLE_KEY

    if not supabase_url or "your-project" in supabase_url or not service_key or "dummy" in service_key:
        print("ℹ️ Clés Supabase non configurées ou fictives dans le .env.")
        print("   -> L'application utilise le stockage local privé par défaut.")
        return False

    buckets = [
        {"id": settings.STORAGE_BUCKET_ORIGINALS, "name": "media-originals", "public": False},
        {"id": settings.STORAGE_BUCKET_PREVIEWS, "name": "media-previews", "public": False},
        {"id": settings.STORAGE_BUCKET_REPORTS, "name": "analysis-reports", "public": False},
    ]

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": "application/json"
    }

    for b in buckets:
        url = f"{supabase_url}/storage/v1/bucket"
        payload = json.dumps(b).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"✅ Bucket privé '{b['id']}' créé avec succès.")
        except urllib.error.HTTPError as e:
            if e.code == 409 or e.code == 400:
                print(f"ℹ️ Bucket privé '{b['id']}' existe déjà.")
            else:
                print(f"⚠️ Information pour le bucket '{b['id']}' : HTTP {e.code}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la création du bucket '{b['id']}' : {e}")

    return True


def check_external_apis():
    print("\n--- 3. Vérification des Clés d'APIs Externes ---")
    
    # Hive AI
    if settings.HIVE_API_KEY:
        print("✅ Clé Hive AI configurée.")
    else:
        print("ℹ️ Clé Hive AI non configurée : le fallback mock intelligent est actif.")

    # Google Fact Check
    if settings.GOOGLE_FACT_CHECK_API_KEY:
        print("✅ Clé Google Fact Check Tools API configurée.")
    else:
        print("ℹ️ Clé Google Fact Check non configurée : le fallback mock intelligent est actif.")

    # Google Vision
    if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
        print("✅ Credentials Google Cloud Vision configurés.")
    else:
        print("ℹ️ Credentials Google Cloud Vision non configurés : le fallback mock intelligent est actif.")


def main():
    print("==================================================================")
    print(" FORENSIC MEDIA — Initialisation & Vérification des Services Distants")
    print("==================================================================")
    check_database_connection()
    setup_supabase_buckets()
    check_external_apis()
    print("\n==================================================================")
    print(" Configuration terminée !")
    print("==================================================================")


if __name__ == "__main__":
    main()
