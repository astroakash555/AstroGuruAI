"""Birth data builder and UTC conversion tests."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

import pytest

from reports.builders import (
    build_birth_context_from_payload,
    build_birth_data_from_context,
    build_birth_data_from_report,
)


def test_build_birth_data_from_report_converts_ist_to_utc() -> None:
    birth_data = build_birth_data_from_report(
        date_of_birth=date(1990, 1, 15),
        birth_time=time(10, 30, 0),
        latitude=28.6139,
        longitude=77.2090,
        timezone_name="Asia/Kolkata",
    )

    assert birth_data.timezone == "Asia/Kolkata"
    assert birth_data.latitude == pytest.approx(28.6139)
    assert birth_data.longitude == pytest.approx(77.2090)
    assert birth_data.datetime_utc == datetime(1990, 1, 15, 5, 0, tzinfo=timezone.utc)


def test_build_birth_data_from_context_uses_ensure_utc() -> None:
    context = build_birth_context_from_payload(
        date_of_birth=date(1990, 1, 15),
        birth_time=time(10, 30, 0),
        birth_place="New Delhi, India",
        timezone_name="Asia/Kolkata",
        latitude=28.6139,
        longitude=77.2090,
    )
    birth_data = build_birth_data_from_context(context)
    assert birth_data.datetime_utc.tzinfo == timezone.utc
    assert birth_data.datetime_utc.hour == 5
