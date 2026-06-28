"""Razorpay API client with test-friendly abstraction."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from backend.app.core.config import Settings
from backend.app.core.exceptions import ValidationError


@dataclass(frozen=True)
class RazorpayOrderResult:
    order_id: str
    amount_paise: int
    currency: str
    receipt: str
    key_id: str


class PaymentGateway(Protocol):
    async def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str] | None = None,
    ) -> RazorpayOrderResult: ...

    def verify_payment_signature(
        self,
        *,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool: ...

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool: ...


class RazorpayGateway:
    """Production Razorpay integration using REST API."""

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if not settings.razorpay_key_id or not settings.razorpay_key_secret:
            raise ValidationError("Razorpay credentials are not configured.")

    async def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str] | None = None,
    ) -> RazorpayOrderResult:
        payload = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": notes or {},
        }
        async with httpx.AsyncClient(
            auth=(self._settings.razorpay_key_id, self._settings.razorpay_key_secret),
            timeout=30.0,
        ) as client:
            response = await client.post(f"{self.BASE_URL}/orders", json=payload)
            response.raise_for_status()
            data = response.json()

        return RazorpayOrderResult(
            order_id=data["id"],
            amount_paise=data["amount"],
            currency=data["currency"],
            receipt=data["receipt"],
            key_id=self._settings.razorpay_key_id,
        )

    def verify_payment_signature(
        self,
        *,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        secret = self._settings.razorpay_key_secret
        if not secret:
            return False
        message = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        digest = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, razorpay_signature)

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        secret = self._settings.razorpay_webhook_secret or self._settings.razorpay_key_secret
        if not secret:
            return False
        digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)


class MockRazorpayGateway:
    """Deterministic gateway for development and tests."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str] | None = None,
    ) -> RazorpayOrderResult:
        order_id = f"order_{uuid.uuid4().hex[:16]}"
        return RazorpayOrderResult(
            order_id=order_id,
            amount_paise=amount_paise,
            currency=currency,
            receipt=receipt,
            key_id=self._settings.razorpay_key_id or "rzp_test_key",
        )

    def verify_payment_signature(
        self,
        *,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        expected = hashlib.sha256(f"{razorpay_order_id}|{razorpay_payment_id}".encode()).hexdigest()
        return razorpay_signature == expected or razorpay_signature == "valid_signature"

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        return signature == "valid_webhook_signature" or signature == hashlib.sha256(payload).hexdigest()


def build_payment_gateway(settings: Settings) -> PaymentGateway:
    if settings.razorpay_enabled and settings.razorpay_key_id and settings.razorpay_key_secret:
        return RazorpayGateway(settings)
    return MockRazorpayGateway(settings)
