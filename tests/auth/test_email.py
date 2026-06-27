"""Tests for auth email delivery."""

from __future__ import annotations

import logging

from backend.app.auth.email import EmailDeliveryService, EmailMessage


def test_send_logs_message(caplog):
    service = EmailDeliveryService()
    with caplog.at_level(logging.INFO):
        service.send(
            EmailMessage(
                to_email="user@example.com",
                subject="Test",
                body="Hello",
            )
        )
    assert "user@example.com" in caplog.text
    assert "Test" in caplog.text


def test_send_password_reset_and_verification(caplog):
    service = EmailDeliveryService()
    with caplog.at_level(logging.INFO):
        service.send_password_reset(to_email="user@example.com", reset_url="http://reset")
        service.send_email_verification(to_email="user@example.com", verify_url="http://verify")
    assert "reset" in caplog.text.lower()
    assert "verify" in caplog.text.lower()
