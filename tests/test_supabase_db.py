import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# URL direct to Supabase
db_urls = [
    "postgresql+psycopg://postgres.qabyrfzkrbqxldfybnid:Q9%2BR%25v3b2ny.Wt.@aws-0-eu-central-1.pooler.supabase.com:6543/postgres",
    "postgresql+psycopg://postgres.qabyrfzkrbqxldfybnid:Q9%2BR%25v3b2ny.Wt.@aws-0-eu-central-1.pooler.supabase.com:5432/postgres",
    "postgresql+psycopg://postgres:Q9%2BR%25v3b2ny.Wt.@db.qabyrfzkrbqxldfybnid.supabase.co:5432/postgres",
]

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.api.app.core.database import Base

success_url = None
for url in db_urls:
    print(f"\n[TEST] Tentative de connexion a : {url.split('@')[1]} ...")
    try:
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).scalar()
            print(f"[OK] Connecte a PostgreSQL Supabase ! Version : {res[:50]}...")
            print("     Creation et migration des 15 tables sur Supabase...")
            Base.metadata.create_all(bind=engine)
            print("[OK] Les 15 tables ont ete creees directement dans votre base Supabase !")
            success_url = url
            break
    except Exception as e:
        print(f"[ECHEC] : {e}")

if success_url:
    print(f"\n[SUCCES TOTAL] La base Supabase est active et migree !")
