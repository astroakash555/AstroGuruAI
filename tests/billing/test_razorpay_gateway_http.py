"""Razorpay gateway HTTP integration tests."""

from __future__ import annotations

import hashlib
import hmac
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.billing.razorpay_client import RazorpayGateway, build_payment_gateway
from backend.app.core.config import Settings


@pytest.mark.asyncio
async def test_razorpay_gateway_create_order(razorpay_settings):
    gateway = RazorpayGateway(razorpay_settings)

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "id": "order_live",
        "amount": 99900,
        "currency": "INR",
        "receipt": "rcpt_1",
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("backend.app.billing.razorpay_client.httpx.AsyncClient", return_value=mock_client):
        order = await gateway.create_order(amount_paise=99900, currency="INR", receipt="rcpt_1")

    assert order.order_id == "order_live"
    assert order.key_id == "rzp_test"


def test_razorpay_gateway_webhook_signature_with_secret(razorpay_settings):
    gateway = RazorpayGateway(razorpay_settings)
    payload = b'{"event":"payment.captured"}'
    signature = hmac.new(b"webhook_secret", payload, hashlib.sha256).hexdigest()
    assert gateway.verify_webhook_signature(payload, signature)


def test_razorpay_gateway_verify_payment_signature_without_secret(razorpay_settings):
    gateway = RazorpayGateway(razorpay_settings)
    gateway._settings = Settings.model_construct(
        razorpay_key_id="rzp_test",
        razorpay_key_secret=None,
        razorpay_webhook_secret=None,
    )
    assert not gateway.verify_payment_signature(
        razorpay_order_id="order_1",
        razorpay_payment_id="pay_1",
        razorpay_signature="anything",
    )


def test_razorpay_gateway_verify_webhook_signature_without_secret(razorpay_settings):
    gateway = RazorpayGateway(razorpay_settings)
    gateway._settings = Settings.model_construct(
        razorpay_key_id="rzp_test",
        razorpay_key_secret=None,
        razorpay_webhook_secret=None,
    )
    assert not gateway.verify_webhook_signature(b"{}", "sig")


def test_build_payment_gateway_uses_razorpay_when_enabled(razorpay_settings):
    gateway = build_payment_gateway(razorpay_settings)
    assert gateway.__class__.__name__ == "RazorpayGateway"
