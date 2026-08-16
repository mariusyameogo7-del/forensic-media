import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.api.app.core.database import SessionLocal, engine, Base
import apps.api.app.models
from apps.api.app.models.user import User
from apps.api.app.models.enums import AccountType, SubscriptionPlan, PaymentOperator, PaymentStatus
from apps.api.app.schemas.payment import PaymentInitiateRequest, PaymentConfirmRequest
from apps.api.app.api.v1.endpoints.payments import initiate_payment, confirm_payment, _detect_card_brand

Base.metadata.create_all(bind=engine)


def test_card_detection_suite():
    print("==================================================")
    print("   TEST DETECTION MARQUE CARTE BANCAIRE & OTP     ")
    print("==================================================")
    
    # 1. Test Unitaire de detection des marques
    assert _detect_card_brand("4485 1234 5678 9012") == "Visa"
    assert _detect_card_brand("5200 1234 5678 9012") == "Mastercard"
    assert _detect_card_brand("2225 1234 5678 9012") == "Mastercard"
    assert _detect_card_brand("3712 1234 5678 9012") == "American Express"
    assert _detect_card_brand("6011 1234 5678 9012") == "Discover"
    print("[OK UNITAIRE] Detection des marques (Visa, Mastercard, AMEX, Discover) validee !")

    db = SessionLocal()
    try:
        test_email = "investigateur_card_brand@forensic.org"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                supabase_user_id="usr_test_card_brand",
                email=test_email,
                account_type=AccountType.STANDARD
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Test Paiement Visa
        card_req_visa = PaymentInitiateRequest(
            plan=SubscriptionPlan.PRO,
            operator=PaymentOperator.CARD,
            card_holder_name="MARIUS YAMEOGO",
            card_number="4485 9999 8888 7777",
            card_expiry="11/29",
            card_cvv="321",
            customer_email=test_email,
        )
        visa_init = initiate_payment(card_req_visa, db, current_user=user)
        print("  Paiement Visa Initie :", visa_init.transaction_ref)
        print("  Label detecte :", visa_init.phone_number)
        assert "Visa" in visa_init.phone_number

        # 3. Test Paiement Mastercard
        card_req_mc = PaymentInitiateRequest(
            plan=SubscriptionPlan.PLUS,
            operator=PaymentOperator.CARD,
            card_holder_name="MARIUS YAMEOGO",
            card_number="5412 1111 2222 3333",
            card_expiry="05/28",
            card_cvv="888",
            customer_email=test_email,
        )
        mc_init = initiate_payment(card_req_mc, db, current_user=user)
        print("  Paiement Mastercard Initie :", mc_init.transaction_ref)
        print("  Label detecte :", mc_init.phone_number)
        assert "Mastercard" in mc_init.phone_number

        # 4. Confirmation 3D-Secure avec l'OTP genere
        mc_confirm = confirm_payment(mc_init.transaction_ref, payload=PaymentConfirmRequest(otp_code=mc_init.demo_otp), db=db, current_user=user)
        print("  [OK VALIDATION 3DS] :", mc_confirm.message_fr)
        assert mc_confirm.is_active == True

    finally:
        db.close()


if __name__ == "__main__":
    test_card_detection_suite()
    print("\n[SUCCES] LA DETECTION AUTOMATIQUE DES CARTES EST 100% VALIDE !")
