from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from apps.api.app.models.enums import SubscriptionPlan, PaymentOperator, PaymentStatus


class PaymentInitiateRequest(BaseModel):
    plan: SubscriptionPlan # "pro" or "plus"
    operator: PaymentOperator # "orange_money", "moov_money", "mtn_momo", "wave", "card"
    phone_number: str
    customer_email: Optional[str] = None
    billing_cycle: Optional[str] = "monthly" # "monthly" or "yearly"


class PaymentInitiateResponse(BaseModel):
    transaction_ref: str
    amount_xof: int
    currency: str = "XOF"
    plan: SubscriptionPlan
    operator: PaymentOperator
    status: PaymentStatus
    instructions_fr: str
    ussd_code: Optional[str] = None
    checkout_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentStatusResponse(BaseModel):
    transaction_ref: str
    status: PaymentStatus
    plan: SubscriptionPlan
    operator: PaymentOperator
    amount_xof: int
    is_active: bool
    message_fr: str
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(BaseModel):
    plan: SubscriptionPlan
    status: str
    monthly_quota: int
    used_quota: int
    remaining_quota: int
    started_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
