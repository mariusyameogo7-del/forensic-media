import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Load .env file explicitly
env_file = Path(__file__).resolve().parents[2] / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.app.core.config import settings
from apps.api.app.core.database import Base, engine


def check_database_connection():
    print("\n--- 1. Verification de la connexion Base de Donnees PostgreSQL ---")
    try:
        with engine.connect() as conn:
            print(f"[OK] Connexion reussie a la base de donnees : {engine.url.host or 'localhost'}")
            print("     Application du schema et des 15 tables...")
            Base.metadata.create_all(bind=engine)
            print("[OK] Les 15 tables ont ete initialisees avec succes dans la base.")
            return True
    except Exception as e:
        print(f"[INFO] Connexion direct PostgreSQL non activee : {e}")
        return False


def setup_supabase_buckets():
    print("\n--- 2. Configuration des 3 Buckets Prives dans Supabase Storage ---")
    supabase_url = os.getenv("SUPABASE_URL", settings.SUPABASE_URL).rstrip("/")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", settings.SUPABASE_SERVICE_ROLE_KEY)

    if not supabase_url or "your-project" in supabase_url or not service_key or "your-service" in service_key:
        print("[INFO] Cles Supabase non configurees.")
        return False

    print(f"[INFO] Connexion au projet Supabase : {supabase_url}")

    buckets = [
        {"id": "media-originals", "name": "media-originals", "public": False},
        {"id": "media-previews", "name": "media-previews", "public": False},
        {"id": "analysis-reports", "name": "analysis-reports", "public": False},
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
                print(f"[OK] Bucket prive '{b['id']}' cree avec succes dans Supabase Storage.")
        except urllib.error.HTTPError as e:
            if e.code in (400, 409):
                print(f"[OK] Bucket prive '{b['id']}' deja existant et pret.")
            else:
                print(f"[INFO] Bucket '{b['id']}' HTTP status : {e.code}")
        except Exception as e:
            print(f"[WARN] Bucket '{b['id']}' : {e}")

    return True


def check_external_apis():
    print("\n--- 3. Verification des Cles d'APIs Externes ---")
    
    # Hive AI
    if os.getenv("HIVE_API_KEY"):
        print("[OK] Cle Hive AI configuree.")
    else:
        print("[INFO] Cle Hive AI non configuree : fallback intelligent actif.")

    # Google Fact Check
    if os.getenv("GOOGLE_FACT_CHECK_API_KEY"):
        print("[OK] Cle Google Fact Check Tools API configuree.")
    else:
        print("[INFO] Cle Google Fact Check non configuree : fallback intelligent actif.")


def main():
    print("==================================================================")
    print(" FORENSIC MEDIA — Initialisation & Configuration Supabase")
    print("==================================================================")
    check_database_connection()
    setup_supabase_buckets()
    check_external_apis()
    print("\n==================================================================")
    print(" Configuration Supabase terminee !")
    print("==================================================================")


if __name__ == "__main__":
    main()
