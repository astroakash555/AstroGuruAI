"""Vimshottari dasha period tree builder."""

from __future__ import annotations

from datetime import datetime, timedelta

from astrology_engine.dasha.balance import (
    lords_from_start,
    next_dasha_lord,
    sub_period_duration_years,
    years_to_days,
)
from astrology_engine.dasha.constants import DAYS_PER_DASHA_YEAR, VIMSHOTTARI_YEARS
from astrology_engine.dasha.types import (
    ActiveDashaPeriod,
    AntardashaPeriod,
    DashaBalance,
    MahadashaPeriod,
    PratyantarDashaPeriod,
)


def _add_years(start: datetime, years: float) -> datetime:
    return start + timedelta(days=years_to_days(years))


def build_pratyantar_dashas(
    antardasha_lord: str,
    start: datetime,
    end: datetime,
) -> tuple[PratyantarDashaPeriod, ...]:
    """Build pratyantar dasha periods within an antardasha."""
    periods: list[PratyantarDashaPeriod] = []
    cursor = start

    for lord in lords_from_start(antardasha_lord):
        if cursor >= end:
            break
        duration_years = sub_period_duration_years(antardasha_lord, lord)
        period_end = min(_add_years(cursor, duration_years), end)
        actual_years = (period_end - cursor).total_seconds() / (DAYS_PER_DASHA_YEAR * 86400.0)
        periods.append(
            PratyantarDashaPeriod(
                lord=lord,
                start=cursor,
                end=period_end,
                duration_years=actual_years,
                duration_days=actual_years * DAYS_PER_DASHA_YEAR,
            )
        )
        cursor = period_end

    return tuple(periods)


def build_antardashas(
    mahadasha_lord: str,
    start: datetime,
    end: datetime,
) -> tuple[AntardashaPeriod, ...]:
    """Build antardasha periods with nested pratyantar dashas."""
    periods: list[AntardashaPeriod] = []
    cursor = start

    for lord in lords_from_start(mahadasha_lord):
        if cursor >= end:
            break
        duration_years = sub_period_duration_years(mahadasha_lord, lord)
        period_end = min(_add_years(cursor, duration_years), end)
        actual_years = (period_end - cursor).total_seconds() / (DAYS_PER_DASHA_YEAR * 86400.0)
        pratyantar_dashas = build_pratyantar_dashas(lord, cursor, period_end)
        periods.append(
            AntardashaPeriod(
                lord=lord,
                start=cursor,
                end=period_end,
                duration_years=actual_years,
                duration_days=actual_years * DAYS_PER_DASHA_YEAR,
                pratyantar_dashas=pratyantar_dashas,
            )
        )
        cursor = period_end

    return tuple(periods)


def build_mahadashas(
    birth_datetime: datetime,
    balance: DashaBalance,
    *,
    max_years: float,
) -> tuple[MahadashaPeriod, ...]:
    """Build mahadasha tree from birth through max_years."""
    periods: list[MahadashaPeriod] = []
    cursor = birth_datetime
    end_limit = _add_years(birth_datetime, max_years)
    current_lord = balance.lord

    # First (balance) mahadasha
    first_end = _add_years(cursor, balance.duration_years)
    first_period = _create_mahadasha_period(current_lord, cursor, first_end)
    periods.append(first_period)
    cursor = first_end
    current_lord = next_dasha_lord(balance.lord)

    while cursor < end_limit:
        full_years = VIMSHOTTARI_YEARS[current_lord]
        period_end = min(_add_years(cursor, full_years), end_limit)
        periods.append(_create_mahadasha_period(current_lord, cursor, period_end))
        cursor = period_end
        current_lord = next_dasha_lord(current_lord)

    return tuple(periods)


def _create_mahadasha_period(lord: str, start: datetime, end: datetime) -> MahadashaPeriod:
    actual_years = (end - start).total_seconds() / (DAYS_PER_DASHA_YEAR * 86400.0)
    return MahadashaPeriod(
        lord=lord,
        start=start,
        end=end,
        duration_years=actual_years,
        duration_days=actual_years * DAYS_PER_DASHA_YEAR,
        antardashas=build_antardashas(lord, start, end),
    )


def find_active_periods(
    mahadashas: tuple[MahadashaPeriod, ...],
    reference: datetime,
) -> dict[str, ActiveDashaPeriod | None]:
    """Locate active mahadasha, antardasha, and pratyantar at reference time."""
    current: dict[str, ActiveDashaPeriod | None] = {
        "mahadasha": None,
        "antardasha": None,
        "pratyantar_dasha": None,
    }

    for mahadasha in mahadashas:
        if not _contains(reference, mahadasha.start, mahadasha.end):
            continue
        current["mahadasha"] = _to_active(mahadasha)
        for antardasha in mahadasha.antardashas:
            if not _contains(reference, antardasha.start, antardasha.end):
                continue
            current["antardasha"] = _to_active(antardasha)
            for pratyantar in antardasha.pratyantar_dashas:
                if _contains(reference, pratyantar.start, pratyantar.end):
                    current["pratyantar_dasha"] = _to_active(pratyantar)
                    break
            break
        break

    return current


def _contains(reference: datetime, start: datetime, end: datetime) -> bool:
    return start <= reference < end


def _to_active(period: MahadashaPeriod | AntardashaPeriod | PratyantarDashaPeriod) -> ActiveDashaPeriod:
    return ActiveDashaPeriod(
        lord=period.lord,
        start=period.start,
        end=period.end,
        duration_years=period.duration_years,
        duration_days=period.duration_days,
    )
