"""Kaal Sarp Dosha detection rule."""

from __future__ import annotations

from astrology_engine.doshas.base import DoshaRule
from astrology_engine.doshas.constants import KAAL_SARP_PLANETS, KAAL_SARP_TYPES
from astrology_engine.doshas.rules._helpers import build_detection, condition
from astrology_engine.doshas.types import DoshaDetection
from astrology_engine.utilities.angles import normalize_longitude
from astrology_engine.yogas.context import ChartContext


class KaalSarpDoshaRule(DoshaRule):
    """
    Kaal Sarp Dosha: all classical planets hemmed between Rahu-Ketu axis.

    Subtype determined by Rahu house placement.
    """

    dosha_id = "kaal_sarp_dosha"
    dosha_name = "Kaal Sarp Dosha"
    category = "karmic"

    def detect(self, context: ChartContext) -> DoshaDetection:
        rahu = context.get_planet("Rahu")
        ketu = context.get_planet("Ketu")
        rahu_house = context.house_of_planet("Rahu")

        enclosed = self._planets_enclosed_by_nodes(context, rahu.longitude, ketu.longitude)
        is_present = len(enclosed) == len(KAAL_SARP_PLANETS)
        subtype = KAAL_SARP_TYPES.get(rahu_house) if is_present else None

        severity = 0.9 if is_present else 0.0
        conditions = [
            condition(
                "all_planets_between_rahu_ketu",
                is_present,
                f"{len(enclosed)}/{len(KAAL_SARP_PLANETS)} classical planets enclosed by nodes.",
            )
        ]
        evidence = []
        if is_present:
            evidence.append(f"All seven classical grahas lie between Rahu and Ketu.")
            evidence.append(f"Kaal Sarp subtype: {subtype} (Rahu in house {rahu_house}).")
        else:
            outside = [name for name in KAAL_SARP_PLANETS if name not in enclosed]
            if outside:
                evidence.append(f"Planets outside node axis: {', '.join(outside)}.")

        return build_detection(
            dosha_id=self.dosha_id,
            dosha_name=self.dosha_name,
            category_key="kaal_sarp_dosha",
            is_present=is_present,
            severity=severity,
            description="Forms when all major planets are enclosed within the Rahu-Ketu axis, indicating karmic intensity.",
            planets=("Rahu", "Ketu", *enclosed),
            houses=(rahu_house, context.house_of_planet("Ketu")),
            conditions=conditions,
            evidence=evidence,
            subtype=subtype,
        )

    @staticmethod
    def _planets_enclosed_by_nodes(
        context: ChartContext,
        rahu_longitude: float,
        ketu_longitude: float,
    ) -> list[str]:
        rahu_lon = normalize_longitude(rahu_longitude)
        ketu_lon = normalize_longitude(ketu_longitude)
        enclosed: list[str] = []

        for planet_name in KAAL_SARP_PLANETS:
            planet_lon = normalize_longitude(context.get_planet(planet_name).longitude)
            if _is_on_rahu_ketu_arc(planet_lon, rahu_lon, ketu_lon):
                enclosed.append(planet_name)

        return enclosed


def _is_on_rahu_ketu_arc(longitude: float, rahu: float, ketu: float) -> bool:
    """Return True when longitude lies on the Rahu→Ketu arc that spans <= 180 degrees."""
    forward_span = (ketu - rahu + 360.0) % 360.0
    reverse_span = (rahu - ketu + 360.0) % 360.0

    if forward_span <= 180.0:
        arc_start, arc_end = rahu, ketu
        span = forward_span
    else:
        arc_start, arc_end = ketu, rahu
        span = reverse_span

    offset = (longitude - arc_start + 360.0) % 360.0
    return 0.0 <= offset <= span
