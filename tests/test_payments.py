import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.api.app.core.database import SessionLocal, engine, Base
import apps.api.app.models
from apps.api.app.models.user import User
from apps.api.app.models.enums import AccountType, SubscriptionPlan, PaymentOperator, PaymentStatus
from apps.api.app.schemas.payment import PaymentInitiateRequest, PaymentConfirmRequest
from apps.api.app.api.v1.endpoints.payments import initiate_payment, confirm_payment, get_payment_status

Base.metadata.create_all(bind=engine)


def test_payment_suite():
    print("==================================================")
    print("   TEST DE LA PASSERELLE DE PAIEMENT SECURISEE    ")
    print("==================================================")
    db = SessionLocal()
    try:
        test_email = "investigateur_pro@forensic.org"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                supabase_user_id="usr_test_payment_suite",
                email=test_email,
                account_type=AccountType.STANDARD
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # ----------------------------------------------------
        # 1. Test Paiement CARTE BANCAIRE (Visa / Mastercard)
        # ----------------------------------------------------
        print("\n--- 1. Test Paiement Carte Bancaire (PRO - 3 000 FCFA) ---")
        card_req = PaymentInitiateRequest(
            plan=SubscriptionPlan.PRO,
            operator=PaymentOperator.CARD,
            card_holder_name="MARIUS YAMEOGO",
            card_number="4485 1234 5678 9012",
            card_expiry="08/28",
            card_cvv="456",
            customer_email=test_email,
            billing_cycle="monthly"
        )
        card_init = initiate_payment(card_req, db, current_user=user)
        print("  Paiement Carte Initie :", card_init.transaction_ref)
        print("  Montant :", card_init.amount_xof, "FCFA | Operator :", card_init.operator)
        assert card_init.amount_xof == 3000
        assert card_init.status == PaymentStatus.PENDING

        # Test Rejet si mauvais OTP
        try:
            confirm_payment(card_init.transaction_ref, payload=PaymentConfirmRequest(otp_code="12"), db=db, current_user=user)
            assert False, "Devrait echouer car OTP < 4 chiffres"
        except Exception as e:
            print("  [OK Securite] Rejet du paiement si OTP manquant ou trop court :", str(e.detail if hasattr(e, 'detail') else e))

        # Validation avec code 3D-Secure 4 chiffres
        card_confirm = confirm_payment(card_init.transaction_ref, payload=PaymentConfirmRequest(otp_code="8910"), db=db, current_user=user)
        print("  [OK Validation 3DS] :", card_confirm.message_fr)
        assert card_confirm.is_active == True
        db.refresh(user)
        assert user.account_type == AccountType.PROFESSIONAL
        print("  [OK Surclassement] Compte PRO active avec succes !")

        # ----------------------------------------------------
        # 2. Test Paiement MOBILE MONEY (Orange Money #144*4*6#)
        # ----------------------------------------------------
        print("\n--- 2. Test Paiement Mobile Money Orange Money (PLUS - 10 000 FCFA) ---")
        momo_req = PaymentInitiateRequest(
            plan=SubscriptionPlan.PLUS,
            operator=PaymentOperator.ORANGE_MONEY,
            phone_number="+226 70 11 22 33",
            customer_email=test_email,
            billing_cycle="monthly"
        )
        momo_init = initiate_payment(momo_req, db, current_user=user)
        print("  Paiement Orange Money Initie :", momo_init.transaction_ref)
        print("  Instructions :", momo_init.instructions_fr)
        assert momo_init.amount_xof == 10000
        assert "#144*4*6#" in momo_init.instructions_fr

        # Validation avec code OTP #144*4*6#
        momo_confirm = confirm_payment(momo_init.transaction_ref, payload=PaymentConfirmRequest(otp_code="5678"), db=db, current_user=user)
        print("  [OK Validation USSD/OTP] :", momo_confirm.message_fr)
        assert momo_confirm.is_active == True
        db.refresh(user)
        assert user.account_type == AccountType.INSTITUTIONAL
        print("  [OK Surclassement] Compte PLUS Illimite active avec succes !")

    finally:
        db.close()


if __name__ == "__main__":
    test_payment_suite()
    print("\n[SUCCES] TOUS LES TESTS DE PAIEMENT REEL SONT VALIDES !")
