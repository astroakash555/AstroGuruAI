"""Tests for Razorpay gateway."""

from __future__ import annotations

import hashlib

import pytest

from backend.app.billing.razorpay_client import MockRazorpayGateway, RazorpayGateway, build_payment_gateway
from backend.app.core.config import Settings
from backend.app.core.exceptions import ValidationError


@pytest.mark.asyncio
async def test_mock_gateway_create_order(billing_settings):
    gateway = MockRazorpayGateway(billing_settings)
    order = await gateway.create_order(amount_paise=99900, currency="INR", receipt="rcpt_1")
    assert order.order_id.startswith("order_")
    assert order.amount_paise == 99900


def test_mock_gateway_verify_payment_signature():
    gateway = MockRazorpayGateway(Settings())
    assert gateway.verify_payment_signature(
        razorpay_order_id="order_1",
        razorpay_payment_id="pay_1",
        razorpay_signature="valid_signature",
    )


def test_mock_gateway_verify_webhook_signature():
    gateway = MockRazorpayGateway(Settings())
    payload = b'{"event":"payment.captured"}'
    assert gateway.verify_webhook_signature(payload, "valid_webhook_signature")


def test_build_payment_gateway_uses_mock_when_disabled(billing_settings):
    gateway = build_payment_gateway(billing_settings)
    assert gateway.__class__.__name__ == "MockRazorpayGateway"


def test_razorpay_gateway_requires_credentials():
    settings = Settings(RAZORPAY_ENABLED="true")
    with pytest.raises(ValidationError):
        RazorpayGateway(settings)


def test_razorpay_gateway_verify_payment_signature(razorpay_settings):
    gateway = RazorpayGateway(razorpay_settings)
    signature = __import__("hmac").new(
        razorpay_settings.razorpay_key_secret.encode(),
        b"order_1|pay_1",
        hashlib.sha256,
    ).hexdigest()
    assert gateway.verify_payment_signature(
        razorpay_order_id="order_1",
        razorpay_payment_id="pay_1",
        razorpay_signature=signature,
    )
