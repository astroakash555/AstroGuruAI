"""Monthly usage counters per subscription metric."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.enums import UsageMetric
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.types import enum_column

if TYPE_CHECKING:
    from backend.app.models.user import User


class UsageQuota(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks monthly consumption for quota enforcement."""

    __tablename__ = "usage_quotas"
    __table_args__ = (
        UniqueConstraint("user_id", "metric", "period_start", name="uq_usage_quotas_user_metric_period"),
        Index("ix_usage_quotas_user_id", "user_id"),
        Index("ix_usage_quotas_period_start", "period_start"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric: Mapped[UsageMetric] = mapped_column(
        enum_column(UsageMetric, "usage_metric"),
        nullable=False,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    user: Mapped[User] = relationship("User", back_populates="usage_quotas")
