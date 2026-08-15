import sys
from pathlib import Path
from sqlalchemy import create_engine, text

regions = [
    "aws-0-eu-central-1", # Frankfurt
    "aws-0-eu-west-1",    # Ireland
    "aws-0-eu-west-3",    # Paris
    "aws-0-eu-north-1",   # Stockholm
    "aws-0-us-east-1",    # N. Virginia
    "aws-0-us-east-2",    # Ohio
    "aws-0-us-west-1",    # N. California
    "aws-0-us-west-2",    # Oregon
    "aws-0-af-south-1",   # Cape Town
    "aws-0-ap-southeast-1", # Singapore
]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apps.api.app.core.database import Base

password = "Q9%2BR%25v3b2ny.Wt."
project_ref = "qabyrfzkrbqxldfybnid"
user = f"postgres.{project_ref}"

found = False
for reg in regions:
    pooler_host = f"{reg}.pooler.supabase.com"
    url = f"postgresql+psycopg://{user}:{password}@{pooler_host}:6543/postgres"
    try:
        engine = create_engine(url, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            v = conn.execute(text("SELECT version();")).scalar()
            print(f"\n[SUCCES] Region Supabase detectee : {reg} !")
            print(f"         PostgreSQL Version : {v[:50]}...")
            print(f"         Creation des 15 tables sur Supabase...")
            Base.metadata.create_all(bind=engine)
            print("[SUCCES] Les 15 tables sont creees et pretes sur votre Supabase !")
            found = True
            
            # Update .env with working URL
            env_path = Path(__file__).resolve().parents[1] / ".env"
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(env_path, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.startswith("DATABASE_URL="):
                        f.write(f'DATABASE_URL="{url}"\n')
                    else:
                        f.write(line)
            print(f"[OK] Fichier .env mis a jour avec la DATABASE_URL exacte.")
            break
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg or "ENOTFOUND" in err_msg:
            continue
        elif "password authentication failed" in err_msg:
            print(f"\n[INFO] Region {reg} detectee, mais verification du mot de passe requise : {e}")
            break
        else:
            continue

if not found:
    print("\n[INFO] Test des regions termine.")
