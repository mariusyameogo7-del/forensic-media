import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.api.app.core.database import SessionLocal, engine, Base
import apps.api.app.models
from apps.api.app.models.user import User
from apps.api.app.models.enums import AccountType, SubscriptionPlan, PaymentOperator, PaymentStatus
from apps.api.app.schemas.payment import PaymentInitiateRequest
from apps.api.app.api.v1.endpoints.payments import initiate_payment, confirm_payment, get_payment_status

# Ensure all tables exist in test database
Base.metadata.create_all(bind=engine)


def test_mobile_money_workflow():
    print("--- 1. Test Initiation Paiement Mobile Money (PRO - 3 000 FCFA) ---")
    db = SessionLocal()
    try:
        # Create test user
        test_email = "journaliste_burkina@presse.bf"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                supabase_user_id="usr_test_pro_momo",
                email=test_email,
                account_type=AccountType.STANDARD
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 1. Initiate Orange Money Pro payment
        req = PaymentInitiateRequest(
            plan=SubscriptionPlan.PRO,
            operator=PaymentOperator.ORANGE_MONEY,
            phone_number="+22670112233",
            customer_email=test_email,
            billing_cycle="monthly"
        )
        init_res = initiate_payment(req, db, current_user=user)
        print("Paiement initié :", init_res.transaction_ref, "| Montant :", init_res.amount_xof, "FCFA")
        assert init_res.amount_xof == 3000
        assert init_res.plan == SubscriptionPlan.PRO
        assert init_res.status == PaymentStatus.PENDING
        assert "144" in init_res.instructions_fr
        print("[OK] Session Orange Money initiée avec succès !")

        # 2. Confirm and Activate Pro Subscription
        confirm_res = confirm_payment(init_res.transaction_ref, otp_code="1234", db=db, current_user=user)
        print("Confirmation :", confirm_res.message_fr)
        assert confirm_res.is_active == True
        assert confirm_res.status == PaymentStatus.COMPLETED

        db.refresh(user)
        assert user.account_type == AccountType.PROFESSIONAL
        print("[OK] Compte utilisateur surclassé en PROFESSIONNEL (Formule PRO active) !")

        # 3. Test Plus Plan Initiation (10 000 FCFA) with Moov Money
        print("\n--- 2. Test Initiation Paiement Mobile Money (PLUS - 10 000 FCFA) ---")
        req_plus = PaymentInitiateRequest(
            plan=SubscriptionPlan.PLUS,
            operator=PaymentOperator.MOOV_MONEY,
            phone_number="+2250102030405",
            customer_email=test_email,
            billing_cycle="monthly"
        )
        init_plus = initiate_payment(req_plus, db, current_user=user)
        assert init_plus.amount_xof == 10000
        assert init_plus.plan == SubscriptionPlan.PLUS
        print("Paiement Plus initié :", init_plus.transaction_ref, "| Montant :", init_plus.amount_xof, "FCFA")

        confirm_plus = confirm_payment(init_plus.transaction_ref, otp_code="5678", db=db, current_user=user)
        assert confirm_plus.is_active == True
        db.refresh(user)
        assert user.account_type == AccountType.INSTITUTIONAL
        print("[OK] Compte utilisateur surclassé en INSTITUTIONNEL (Formule PLUS active - Illimité) !")

    finally:
        db.close()


if __name__ == "__main__":
    test_mobile_money_workflow()
    print("\nTOUS LES TESTS DU MODULE MOBILE MONEY SONT VALIDÉS !")
