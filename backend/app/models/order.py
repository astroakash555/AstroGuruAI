"""Billing order model for Razorpay checkout."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import OrderStatus, SubscriptionPlan
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.payment import Payment
    from backend.app.models.user import User


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Checkout order created before payment capture."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        UniqueConstraint("razorpay_order_id", name="uq_orders_razorpay_order_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        enum_column(SubscriptionPlan, "subscription_plan"),
        nullable=False,
    )
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", server_default="INR", nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        enum_column(OrderStatus, "order_status"),
        default=OrderStatus.CREATED,
        server_default=OrderStatus.CREATED.value,
        nullable=False,
    )
    razorpay_order_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    receipt: Mapped[str] = mapped_column(String(128), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="orders")
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="order")
