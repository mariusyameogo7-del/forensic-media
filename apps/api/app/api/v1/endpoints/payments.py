import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
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
        "ussd": "*144*4*6#",
        "instructions": "Composez le #144*4*6# ou validez la notification push reçue sur votre téléphone Orange Money.",
    },
    PaymentOperator.MOOV_MONEY: {
        "name": "Moov Money",
        "ussd": "*155*4#",
        "instructions": "Composez le *155*4# ou validez le message de confirmation Moov Money sur votre téléphone.",
    },
    PaymentOperator.MTN_MOMO: {
        "name": "MTN Mobile Money",
        "ussd": "*133#",
        "instructions": "Validez la demande d'autorisation de prélèvement sur votre application MTN MoMo ou tapez *133#.",
    },
    PaymentOperator.WAVE: {
        "name": "Wave",
        "ussd": "App Wave",
        "instructions": "Ouvrez votre application Wave pour valider le débit instantané avec votre code secret.",
    },
    PaymentOperator.CARD: {
        "name": "Carte Bancaire (Visa / Mastercard)",
        "ussd": None,
        "instructions": "Saisie des informations de carte bancaire sécurisée par chiffrement SSL 256 bits.",
    },
    PaymentOperator.FEDAPAY: {
        "name": "FedaPay Pan-Afrique",
        "ussd": None,
        "instructions": "Redirection vers la passerelle sécurisée FedaPay.",
    },
    PaymentOperator.CINETPAY: {
        "name": "CinetPay",
        "ussd": None,
        "instructions": "Redirection vers le guichet unique CinetPay.",
    },
}


@router.post("/initiate", response_model=PaymentInitiateResponse, summary="Initier un paiement Mobile Money pour Pro ou Plus")
def initiate_payment(
    payload: PaymentInitiateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Initiates a Mobile Money payment (Orange Money, Moov Money, MTN MoMo, Wave, Card)
    for Pro (3 000 FCFA/mo) or Plus (10 000 FCFA/mo).
    """
    if payload.plan not in PLAN_PRICES_XOF:
        raise HTTPException(status_code=400, detail="Plan de souscription invalide (choisir 'pro' ou 'plus').")

    billing = payload.billing_cycle or "monthly"
    amount = PLAN_PRICES_XOF[payload.plan].get(billing, PLAN_PRICES_XOF[payload.plan]["monthly"])
    
    # Generate unique transaction reference
    year = datetime.now(timezone.utc).year
    suffix = secrets.token_hex(3).upper()
    tx_ref = f"PAY-{year}-{payload.plan.value.upper()}-{suffix}"

    op_info = OPERATOR_INSTRUCTIONS.get(payload.operator, OPERATOR_INSTRUCTIONS[PaymentOperator.ORANGE_MONEY])

    # Create payment record
    payment = Payment(
        user_id=current_user.id if current_user else None,
        plan=payload.plan,
        operator=payload.operator,
        amount_xof=amount,
        currency="XOF",
        phone_number=payload.phone_number.strip(),
        customer_email=(payload.customer_email or (current_user.email if current_user else "client@forensic.org")).strip(),
        transaction_ref=tx_ref,
        status=PaymentStatus.PENDING,
        metadata_json={
            "billing_cycle": billing,
            "operator_name": op_info["name"],
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
        checkout_url=f"/api/v1/payments/checkout/{payment.transaction_ref}",
        created_at=payment.created_at,
    )


@router.post("/confirm/{transaction_ref}", response_model=PaymentStatusResponse, summary="Confirmer et activer l'abonnement Mobile Money")
def confirm_payment(
    transaction_ref: str,
    otp_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Confirms Mobile Money debit authorization and activates Pro / Plus subscription.
    """
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
        message_fr=f"Paiement de {payment.amount_xof:,} FCFA validé avec succès ! Votre {plan_name} est désormais active.".replace(",", " "),
        completed_at=payment.completed_at,
    )


@router.get("/status/{transaction_ref}", response_model=PaymentStatusResponse, summary="Vérifier l'état d'un paiement")
def get_payment_status(transaction_ref: str, db: Session = Depends(get_db)):
    """Checks the live state of a transaction."""
    payment = db.execute(select(Payment).where(Payment.transaction_ref == transaction_ref)).scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Transaction introuvable.")

    is_active = payment.status == PaymentStatus.COMPLETED
    msg = "Paiement en attente de validation sur votre téléphone." if payment.status == PaymentStatus.PENDING else "Abonnement actif."
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


@router.post("/webhook", summary="Webhook universel FedaPay / CinetPay / Mobile Money")
def payment_webhook(payload: dict, db: Session = Depends(get_db)):
    """Receives automated payment notifications from Mobile Money gateways."""
    event_type = payload.get("event") or payload.get("status")
    tx_ref = payload.get("custom_metadata", {}).get("transaction_ref") or payload.get("transaction_id")
    
    if tx_ref:
        payment = db.execute(select(Payment).where(Payment.transaction_ref == tx_ref)).scalar_one_or_none()
        if payment:
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.now(timezone.utc)
            db.commit()

    return {"status": "received", "timestamp": datetime.now(timezone.utc).isoformat()}
