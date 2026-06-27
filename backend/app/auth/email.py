"""Provider-agnostic email delivery for auth flows."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailMessage:
    to_email: str
    subject: str
    body: str


class EmailDeliveryService:
    """Logs emails in development and can be swapped for SMTP/SES later."""

    def send(self, message: EmailMessage) -> None:
        logger.info(
            "Auth email queued to=%s subject=%s body=%s",
            message.to_email,
            message.subject,
            message.body,
        )

    def send_password_reset(self, *, to_email: str, reset_url: str) -> None:
        self.send(
            EmailMessage(
                to_email=to_email,
                subject="Reset your AstroGuruAI password",
                body=f"Use this link to reset your password: {reset_url}",
            )
        )

    def send_email_verification(self, *, to_email: str, verify_url: str) -> None:
        self.send(
            EmailMessage(
                to_email=to_email,
                subject="Verify your AstroGuruAI account",
                body=f"Confirm your email address: {verify_url}",
            )
        )
