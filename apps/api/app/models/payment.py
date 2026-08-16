import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, ForeignKey, Uuid, JSON
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base
from apps.api.app.models.enums import SubscriptionPlan, PaymentStatus, PaymentOperator


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    plan = Column(SQLEnum(SubscriptionPlan, native_enum=False), nullable=False)
    operator = Column(SQLEnum(PaymentOperator, native_enum=False), nullable=False)
    amount_xof = Column(Integer, nullable=False)
    currency = Column(String(10), default="XOF", nullable=False)
    phone_number = Column(String(50), nullable=True)
    customer_email = Column(String(255), nullable=True)
    transaction_ref = Column(String(100), unique=True, nullable=False, index=True)
    gateway_ref = Column(String(255), nullable=True)
    status = Column(SQLEnum(PaymentStatus, native_enum=False), default=PaymentStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, nullable=True)

    # Relationship
    user = relationship("User", foreign_keys=[user_id])


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionPlan, native_enum=False), default=SubscriptionPlan.TRIAL, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    monthly_quota = Column(Integer, default=3, nullable=False) # -1 for unlimited (Plus), 100 for Pro, 3 for trial
    used_quota = Column(Integer, default=0, nullable=False)
    last_payment_id = Column(Uuid, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    last_payment = relationship("Payment", foreign_keys=[last_payment_id])
