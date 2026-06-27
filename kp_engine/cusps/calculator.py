"""KP cuspal analysis."""

from __future__ import annotations

from astrology_engine.core.types import BhavaChart, VedicChartBundle
from kp_engine.lords import get_sub_lord
from kp_engine.types import CuspalPoint


def analyze_cusps(chart: VedicChartBundle) -> tuple[CuspalPoint, ...]:
    """Analyze bhava cusps with KP star and sub lords."""
    bhava: BhavaChart = chart.bhava_chart
    cusps: list[CuspalPoint] = []

    for cusp in bhava.house_cusps:
        _, star_lord, sub_lord = get_sub_lord(cusp.longitude)
        cusps.append(
            CuspalPoint(
                house=cusp.number,
                longitude=cusp.longitude,
                sign=cusp.sign.name_en,
                star_lord=star_lord,
                sub_lord=sub_lord,
            )
        )

    return tuple(cusps)
