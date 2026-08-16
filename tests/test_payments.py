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


def test_strict_otp_suite():
    print("==================================================")
    print("   TEST VERIFICATION STRICTE OTP LIE AU NUMERO   ")
    print("==================================================")
    db = SessionLocal()
    try:
        test_email = "investigateur_strict@forensic.org"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                supabase_user_id="usr_test_strict_otp",
                email=test_email,
                account_type=AccountType.STANDARD
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 1. Initiation Mobile Money Orange Money
        phone = "+226 70 99 88 77"
        momo_req = PaymentInitiateRequest(
            plan=SubscriptionPlan.PRO,
            operator=PaymentOperator.ORANGE_MONEY,
            phone_number=phone,
            customer_email=test_email,
            billing_cycle="monthly"
        )
        init_res = initiate_payment(momo_req, db, current_user=user)
        generated_otp = init_res.demo_otp
        print("  Paiement Initie :", init_res.transaction_ref)
        print("  Numero de telephone lie :", init_res.phone_number)
        print("  OTP dynamique genere pour ce numero :", generated_otp)
        assert generated_otp is not None and len(generated_otp) == 4

        # 2. Test Saisie d'un FAUX OTP (ex: 0000) -> DOIT ETRE STRICTEMENT REJETE
        print("\n--- Test Saisie Faux OTP (0000) ---")
        try:
            confirm_payment(init_res.transaction_ref, payload=PaymentConfirmRequest(otp_code="0000"), db=db, current_user=user)
            assert False, "Erreur : Le faux OTP n'aurait jamais du passer !"
        except Exception as e:
            detail = str(e.detail if hasattr(e, 'detail') else e)
            print("  [OK REJET STRICT DU FAUX OTP] :", detail)
            assert "incorrect" in detail

        # 3. Test Saisie du BON OTP LIE AU TELEPHONE -> DOIT REUSSIR
        print("\n--- Test Saisie du VRAI OTP lié au numéro (" + generated_otp + ") ---")
        success_res = confirm_payment(init_res.transaction_ref, payload=PaymentConfirmRequest(otp_code=generated_otp), db=db, current_user=user)
        print("  [OK VALIDATION] :", success_res.message_fr)
        assert success_res.is_active == True
        assert success_res.status == PaymentStatus.COMPLETED

        db.refresh(user)
        assert user.account_type == AccountType.PROFESSIONAL
        print("  [OK SURCLASSEMENT] Le compte PRO a ete active avec succes !")

    finally:
        db.close()


if __name__ == "__main__":
    test_strict_otp_suite()
    print("\n[SUCCES] LA VERIFICATION STRICTE DU CODE OTP EST VALIDE A 100% !")
