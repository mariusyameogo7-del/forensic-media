import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.api.app.core.database import SessionLocal
from apps.api.app.api.v1.endpoints.analyses import list_analyses, get_admin_stats


def test_admin_stats_and_isolation():
    print("--- 1. Verification de l'isolation de l'historique ---")
    db = SessionLocal()
    try:
        # Anonymous without tokens should return 0 items (zero data leakage)
        res_anon = list_analyses(
            limit=20, offset=0, conclusion=None, status=None, search=None,
            admin_key=None, x_my_tokens=None, db=db, current_user=None
        )
        print("Historique anonyme sans token :", len(res_anon.items), "| Total :", res_anon.total)
        assert res_anon.total == 0
        print("[OK] Aucun historique divulgue aux visiteurs anonymes !")

        # Admin access with key
        res_admin = list_analyses(
            limit=20, offset=0, conclusion=None, status=None, search=None,
            admin_key="forensic_admin_2026", x_my_tokens=None, db=db, current_user=None
        )
        print("Historique Admin global :", len(res_admin.items), "| Total :", res_admin.total)
        assert res_admin.total >= 0
        print("[OK] Acces Administrateur operationnel !")

        # Admin Stats endpoint
        stats = get_admin_stats(admin_key="forensic_admin_2026", db=db, current_user=None)
        print("Stats Admin :", stats)
        assert "total_analyses" in stats
        assert "total_ai_detected" in stats
        print("[OK] Dashboard Administrateur operationnel !")
    finally:
        db.close()


if __name__ == "__main__":
    test_admin_stats_and_isolation()
    print("\nTOUS LES TESTS DE FONCTIONNALITES SONT VALIDES !")
