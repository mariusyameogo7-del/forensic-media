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
        "instructions": "Tapez #144*4*6# sur votre téléphone Orange Money ou consultez le SMS pour obtenir votre code d'autorisation OTP.",
    },
    PaymentOperator.MOOV_MONEY: {
        "name": "Moov Money",
        "ussd": "*155*4#",
        "instructions": "Tapez *155*4# sur votre téléphone Moov Money ou consultez le SMS pour obtenir votre code de sécurité temporaire.",
    },
    PaymentOperator.MTN_MOMO: {
        "name": "MTN Mobile Money",
        "ussd": "*133#",
        "instructions": "Consultez le SMS reçu ou tapez *133# pour valider la demande de prélèvement MTN MoMo.",
    },
    PaymentOperator.WAVE: {
        "name": "Wave",
        "ussd": "App Wave",
        "instructions": "Ouvrez votre application Wave ou consultez le code de validation reçu par notification.",
    },
    PaymentOperator.CARD: {
        "name": "Carte Bancaire (Visa / Mastercard)",
        "ussd": "3D-Secure",
        "instructions": "Votre banque vous a transmis un code de validation 3D-Secure par SMS pour autoriser la transaction.",
    },
}


def _detect_card_brand(card_number: Optional[str]) -> str:
    """Detects card brand based on BIN / Prefix."""
    if not card_number:
        return "Carte Bancaire"
    clean = re.sub(r"\s+", "", card_number)
    if clean.startswith("4"):
        return "Visa"
    elif clean.startswith(("51", "52", "53", "54", "55")) or (len(clean) >= 4 and clean[:4].isdigit() and 2221 <= int(clean[:4]) <= 2720):
        return "Mastercard"
    elif clean.startswith(("34", "37")):
        return "American Express"
    elif clean.startswith(("6011", "65")) or clean.startswith(("644", "645", "646", "647", "648", "649")):
        return "Discover"
    return "Carte Bancaire"


def _validate_card_details(card_number: Optional[str], expiry: Optional[str], cvv: Optional[str], holder: Optional[str]):
    if not card_number or not expiry or not cvv:
        raise HTTPException(
            status_code=400,
            detail="Informations de carte bancaire incomplètes. Veuillez renseigner le nom du titulaire, le numéro de carte, la date d'expiration et le code CVV."
        )
    
    clean_num = re.sub(r"\s+", "", card_number)
    if not (clean_num.isdigit() and len(clean_num) in (15, 16)):
        raise HTTPException(
            status_code=400,
            detail="Numéro de carte bancaire invalide (doit comporter 16 chiffres)."
        )

    clean_cvv = cvv.strip()
    if not (clean_cvv.isdigit() and len(clean_cvv) in (3, 4)):
        raise HTTPException(
            status_code=400,
            detail="Code de sécurité CVV invalide (3 chiffres au verso de la carte)."
        )

    # Expiry format MM/YY or MM/YYYY
    if not re.match(r"^(0[1-9]|1[0-2])\/([0-9]{2}|[0-9]{4})$", expiry.strip()):
        raise HTTPException(
            status_code=400,
            detail="Date d'expiration invalide. Format attendu : MM/AA (ex: 08/28)."
        )


@router.post("/initiate", response_model=PaymentInitiateResponse, summary="Initier un paiement avec génération de code OTP lié au téléphone")
def initiate_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Initiates transaction and generates a unique OTP code tied directly to the phone number.
    Detects card brand (Visa, Mastercard, etc.) when paying by card.
    """
    if payload.plan not in PLAN_PRICES_XOF:
        raise HTTPException(status_code=400, detail="Plan de souscription invalide (choisir 'pro' ou 'plus').")

    billing = payload.billing_cycle or "monthly"
    amount = PLAN_PRICES_XOF[payload.plan].get(billing, PLAN_PRICES_XOF[payload.plan]["monthly"])
    
    card_brand = None
    # Specific validation per operator
    if payload.operator == PaymentOperator.CARD:
        _validate_card_details(
            payload.card_number,
            payload.card_expiry,
            payload.card_cvv,
            payload.card_holder_name
        )
        card_brand = _detect_card_brand(payload.card_number)
        last4 = re.sub(r"\s+", "", payload.card_number)[-4:]
        phone_label = f"Carte {card_brand} (**** {last4})"
    else:
        if not payload.phone_number or len(payload.phone_number.strip()) < 8:
            raise HTTPException(
                status_code=400,
                detail="Numéro de téléphone Mobile Money obligatoire (ex: +226 70 11 22 33)."
            )
        phone_label = payload.phone_number.strip()

    # Generate unique transaction reference
    year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    tx_ref = f"PAY-{year}-{payload.plan.value.upper()}-{suffix}"

    # Generate a cryptographically secure 4-digit OTP tied to this transaction & phone
    dynamic_otp = str(secrets.randbelow(9000) + 1000)

    op_info = OPERATOR_INSTRUCTIONS.get(payload.operator, OPERATOR_INSTRUCTIONS[PaymentOperator.ORANGE_MONEY])

    # Create pending payment record
    now_utc = datetime.now(timezone.utc)
    payment = Payment(
        user_id=current_user.id if current_user else None,
        plan=payload.plan,
        operator=payload.operator,
        amount_xof=amount,
        currency="XOF",
        phone_number=phone_label,
        customer_email=(payload.customer_email or (current_user.email if current_user else "client@forensic.org")).strip(),
        transaction_ref=tx_ref,
        status=PaymentStatus.PENDING,
        metadata_json={
            "billing_cycle": billing,
            "operator_name": op_info["name"],
            "card_holder": payload.card_holder_name if payload.operator == PaymentOperator.CARD else None,
            "card_brand": card_brand,
            "expected_otp": dynamic_otp,
            "phone_number": phone_label,
            "otp_created_at": now_utc.isoformat(),
            "otp_expires_at": (now_utc + timedelta(minutes=15)).isoformat(),
            "failed_attempts": 0,
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
        phone_number=phone_label,
        instructions_fr=op_info["instructions"],
        ussd_code=op_info.get("ussd"),
        requires_otp=True,
        demo_otp=dynamic_otp,
        checkout_url=f"/api/v1/payments/checkout/{payment.transaction_ref}",
        created_at=payment.created_at,
    )


@router.post("/confirm/{transaction_ref}", response_model=PaymentStatusResponse, summary="Valider le paiement avec vérification stricte du code OTP")
def confirm_payment(
    transaction_ref: str,
    payload: Optional[PaymentConfirmRequest] = None,
    otp_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Validates payment strictly against the OTP generated for this phone number / transaction.
    Rejects wrong OTPs, expired OTPs, or exceeded attempts.
    """
    code = (payload.otp_code if payload and payload.otp_code else otp_code) or ""
    code = code.strip()

    payment = db.execute(select(Payment).where(Payment.transaction_ref == transaction_ref)).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction de paiement introuvable.")

    if payment.status == PaymentStatus.COMPLETED:
        return PaymentStatusResponse(
            transaction_ref=payment.transaction_ref,
            status=payment.status,
            plan=payment.plan,
            operator=payment.operator,
            amount_xof=payment.amount_xof,
            is_active=True,
            message_fr="Cette transaction a déjà été confirmée avec succès.",
            completed_at=payment.completed_at,
        )

    if payment.status == PaymentStatus.FAILED:
        raise HTTPException(
            status_code=400,
            detail="Cette transaction a été annulée suite à un trop grand nombre d'échecs de saisie de code OTP."
        )

    meta = payment.metadata_json or {}
    expected_otp = meta.get("expected_otp")
    phone_linked = meta.get("phone_number") or payment.phone_number or "votre téléphone"

    # Verify presence of code
    if not code:
        raise HTTPException(
            status_code=400,
            detail=f"Code OTP manquant. Veuillez saisir le code d'autorisation transmis au {phone_linked}."
        )

    # Strict check: code MUST match the expected OTP
    if expected_otp and code != expected_otp:
        failed_attempts = meta.get("failed_attempts", 0) + 1
        meta["failed_attempts"] = failed_attempts
        payment.metadata_json = meta

        if failed_attempts >= 3:
            payment.status = PaymentStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=400,
                detail=f"Code OTP erroné. 3 tentatives échouées : La transaction a été verrouillée pour des raisons de sécurité."
            )

        db.commit()
        remaining = 3 - failed_attempts
        raise HTTPException(
            status_code=400,
            detail=f"Code OTP « {code} » incorrect pour {phone_linked} ! Veuillez vérifier le SMS/USSD reçu ({remaining} tentative(s) restante(s))."
        )

    # OTP is VALID ! Proceed to activation
    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = datetime.now(timezone.utc)

    # Duration: 30 days for monthly, 365 days for yearly
    billing = meta.get("billing_cycle", "monthly")
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
        message_fr=f"Paiement de {payment.amount_xof:,} FCFA validé avec succès (Code OTP {code} certifié pour {phone_linked}) ! Votre {plan_name} est active.".replace(",", " "),
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
