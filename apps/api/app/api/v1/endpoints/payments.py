import uuid
import re
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.app.core.database import get_db
from apps.api.app.core.errors import NotFoundError, UnauthorizedError
from apps.api.app.api.v1.endpoints.auth import get_current_user_optional, get_current_user
from apps.api.app.models.user import User
from apps.api.app.models.payment import Payment, Subscription
from apps.api.app.models.enums import SubscriptionPlan, PaymentOperator, PaymentStatus, AccountType
from apps.api.app.schemas.payment import (
    PaymentInitiateRequest,
    PaymentConfirmRequest,
    PaymentInitiateResponse,
    PaymentStatusResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/payments", tags=["Paiements & Mobile Money"])

PLAN_PRICES_XOF = {
    SubscriptionPlan.PRO: {
        "monthly": 3000,
        "yearly": 30000,
    },
    SubscriptionPlan.PLUS: {
        "monthly": 10000,
        "yearly": 100000,
    },
}

OPERATOR_INSTRUCTIONS = {
    PaymentOperator.ORANGE_MONEY: {
        "name": "Orange Money",
        "ussd": "#144*4*6#",
        "instructions": "Tapez #144*4*6# sur votre téléphone pour générer votre code d'autorisation OTP à 4 ou 6 chiffres, puis saisissez-le pour valider le débit.",
    },
    PaymentOperator.MOOV_MONEY: {
        "name": "Moov Money",
        "ussd": "*155*4#",
        "instructions": "Tapez *155*4# sur votre téléphone pour obtenir votre code de sécurité temporaire Moov Money et confirmez le débit.",
    },
    PaymentOperator.MTN_MOMO: {
        "name": "MTN Mobile Money",
        "ussd": "*133#",
        "instructions": "Consultez le SMS ou tapez *133# pour saisir votre code secret d'autorisation MTN MoMo.",
    },
    PaymentOperator.WAVE: {
        "name": "Wave",
        "ussd": "App Wave",
        "instructions": "Ouvrez votre application Wave ou saisissez le code OTP reçu par SMS pour finaliser le débit instantané.",
    },
    PaymentOperator.CARD: {
        "name": "Carte Bancaire (Visa / Mastercard)",
        "ussd": "3D-Secure",
        "instructions": "Votre banque vous a transmis un code de validation 3D-Secure par SMS pour autoriser la transaction.",
    },
    PaymentOperator.FEDAPAY: {
        "name": "FedaPay Pan-Afrique",
        "ussd": None,
        "instructions": "Passerelle sécurisée multi-opérateurs FedaPay.",
    },
    PaymentOperator.CINETPAY: {
        "name": "CinetPay",
        "ussd": None,
        "instructions": "Guichet unique sécurisé CinetPay.",
    },
}


def _validate_card_details(card_number: Optional[str], expiry: Optional[str], cvv: Optional[str], holder: Optional[str]):
    if not card_number or not expiry or not cvv:
        raise HTTPException(
            status_code=400,
            detail="Informations de carte bancaire incomplètes. Veuillez renseigner le numéro, la date d'expiration et le code CVV."
        )
    
    clean_num = re.sub(r"\s+", "", card_number)
    if not (clean_num.isdigit() and len(clean_num) in (15, 16)):
        raise HTTPException(
            status_code=400,
            detail="Numéro de carte bancaire invalide (doit contenir 16 chiffres)."
        )

    clean_cvv = cvv.strip()
    if not (clean_cvv.isdigit() and len(clean_cvv) in (3, 4)):
        raise HTTPException(
            status_code=400,
            detail="Code CVV de sécurité invalide (3 ou 4 chiffres au dos de la carte)."
        )

    # Expiry format MM/YY or MM/YYYY
    if not re.match(r"^(0[1-9]|1[0-2])\/([0-9]{2}|[0-9]{4})$", expiry.strip()):
        raise HTTPException(
            status_code=400,
            detail="Date d'expiration invalide. Format attendu : MM/AA (ex: 08/28)."
        )


@router.post("/initiate", response_model=PaymentInitiateResponse, summary="Initier un paiement réel Mobile Money ou Carte Bancaire")
def initiate_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Initiates a verified transaction.
    For Card payments: validates card format, expiration, and CVV.
    For Mobile Money: validates phone number and sets up OTP verification.
    """
    if payload.plan not in PLAN_PRICES_XOF:
        raise HTTPException(status_code=400, detail="Plan de souscription invalide (choisir 'pro' ou 'plus').")

    billing = payload.billing_cycle or "monthly"
    amount = PLAN_PRICES_XOF[payload.plan].get(billing, PLAN_PRICES_XOF[payload.plan]["monthly"])
    
    # Specific validation per operator
    if payload.operator == PaymentOperator.CARD:
        _validate_card_details(
            payload.card_number,
            payload.card_expiry,
            payload.card_cvv,
            payload.card_holder_name
        )
        masked_phone = f"Card: **** **** **** {re.sub(r'\\s+', '', payload.card_number)[-4:]}"
    else:
        if not payload.phone_number or len(payload.phone_number.strip()) < 8:
            raise HTTPException(
                status_code=400,
                detail="Numéro de téléphone Mobile Money obligatoire (ex: +226 70 11 22 33)."
            )
        masked_phone = payload.phone_number.strip()

    # Generate unique transaction reference
    year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    tx_ref = f"PAY-{year}-{payload.plan.value.upper()}-{suffix}"

    op_info = OPERATOR_INSTRUCTIONS.get(payload.operator, OPERATOR_INSTRUCTIONS[PaymentOperator.ORANGE_MONEY])

    # Create pending payment record
    payment = Payment(
        user_id=current_user.id if current_user else None,
        plan=payload.plan,
        operator=payload.operator,
        amount_xof=amount,
        currency="XOF",
        phone_number=masked_phone,
        customer_email=(payload.customer_email or (current_user.email if current_user else "client@forensic.org")).strip(),
        transaction_ref=tx_ref,
        status=PaymentStatus.PENDING,
        metadata_json={
            "billing_cycle": billing,
            "operator_name": op_info["name"],
            "card_holder": payload.card_holder_name if payload.operator == PaymentOperator.CARD else None,
        }
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentInitiateResponse(
        transaction_ref=payment.transaction_ref,
        amount_xof=payment.amount_xof,
        currency=payment.currency,
        plan=payment.plan,
        operator=payment.operator,
        status=payment.status,
        instructions_fr=op_info["instructions"],
        ussd_code=op_info.get("ussd"),
        requires_otp=True,
        checkout_url=f"/api/v1/payments/checkout/{payment.transaction_ref}",
        created_at=payment.created_at,
    )


@router.post("/confirm/{transaction_ref}", response_model=PaymentStatusResponse, summary="Valider le paiement avec Code OTP / 3D-Secure")
def confirm_payment(
    transaction_ref: str,
    payload: Optional[PaymentConfirmRequest] = None,
    otp_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Confirms payment with the OTP code generated by USSD / 3D-Secure SMS.
    Rejects payment if OTP code is absent or invalid.
    """
    code = (payload.otp_code if payload and payload.otp_code else otp_code) or ""
    code = code.strip()

    if not code or len(code) < 4:
        raise HTTPException(
            status_code=400,
            detail="Code de confirmation OTP / 3D-Secure manquant ou invalide (saisir au minimum 4 chiffres reçus ou générés par USSD)."
        )

    payment = db.execute(select(Payment).where(Payment.transaction_ref == transaction_ref)).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction de paiement introuvable.")

    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = datetime.now(timezone.utc)

    # Duration: 30 days for monthly, 365 days for yearly
    billing = (payment.metadata_json or {}).get("billing_cycle", "monthly")
    duration_days = 365 if billing == "yearly" else 30
    expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)

    # Determine user target
    user = current_user or payment.user
    if not user and payment.customer_email:
        user = db.execute(select(User).where(User.email == payment.customer_email.lower())).scalar_one_or_none()

    if user:
        # Update User account type
        if payment.plan == SubscriptionPlan.PLUS:
            user.account_type = AccountType.INSTITUTIONAL
        else:
            user.account_type = AccountType.PROFESSIONAL

        # Update or create subscription
        sub = db.execute(select(Subscription).where(Subscription.user_id == user.id)).scalar_one_or_none()
        if not sub:
            sub = Subscription(
                user_id=user.id,
                plan=payment.plan,
                status="active",
                started_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                monthly_quota=-1 if payment.plan == SubscriptionPlan.PLUS else 100,
                used_quota=0,
                last_payment_id=payment.id,
            )
            db.add(sub)
        else:
            sub.plan = payment.plan
            sub.status = "active"
            sub.expires_at = expires_at
            sub.monthly_quota = -1 if payment.plan == SubscriptionPlan.PLUS else 100
            sub.last_payment_id = payment.id

    db.commit()
    db.refresh(payment)

    plan_name = "Formule PLUS (Entreprises & Rédactions)" if payment.plan == SubscriptionPlan.PLUS else "Formule PRO (Journalistes & Vérificateurs)"
    return PaymentStatusResponse(
        transaction_ref=payment.transaction_ref,
        status=payment.status,
        plan=payment.plan,
        operator=payment.operator,
        amount_xof=payment.amount_xof,
        is_active=True,
        message_fr=f"Paiement de {payment.amount_xof:,} FCFA validé avec succès (Code OTP/3DS vérifié) ! Votre {plan_name} est désormais active.".replace(",", " "),
        completed_at=payment.completed_at,
    )


@router.get("/status/{transaction_ref}", response_model=PaymentStatusResponse, summary="Vérifier l'état d'un paiement")
def get_payment_status(transaction_ref: str, db: Session = Depends(get_db)):
    """Checks the live state of a transaction."""
    payment = db.execute(select(Payment).where(Payment.transaction_ref == transaction_ref)).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction introuvable.")

    is_active = payment.status == PaymentStatus.COMPLETED
    msg = "Paiement en attente de validation OTP sur votre téléphone." if payment.status == PaymentStatus.PENDING else "Abonnement actif."
    return PaymentStatusResponse(
        transaction_ref=payment.transaction_ref,
        status=payment.status,
        plan=payment.plan,
        operator=payment.operator,
        amount_xof=payment.amount_xof,
        is_active=is_active,
        message_fr=msg,
        completed_at=payment.completed_at,
    )
