"""Bootstrap golden chart reference data from the astrology engine.

Reference values are locked to Lahiri ayanamsa, whole-sign houses, and mean node
(AstroSage/JHora compatible defaults). Charts marked ``astrosage`` were manually
verified against AstroSage; others are engine-locked baselines pending external audit.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

from astrology_engine import VedicAstrologyEngine
from astrology_engine.dasha.serializer import to_json_dict
from tests.golden.helpers import build_birth_data, build_dasha_input_from_bundle

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DIR = ROOT / "tests" / "fixtures" / "golden_charts"
CHARTS_DIR = GOLDEN_DIR / "charts"

DASHA_REFERENCE = datetime(2026, 6, 28, 12, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class ChartSeed:
    chart_id: str
    name: str
    date_of_birth: date
    birth_time: time
    timezone: str
    latitude: float
    longitude: float
    place: str
    source: str
    notes: str = ""


CHART_SEEDS: tuple[ChartSeed, ...] = (
    ChartSeed(
        "poorvi_sharma_2016",
        "Poorvi Sharma",
        date(2016, 6, 14),
        time(15, 15),
        "Asia/Kolkata",
        28.6138954,
        77.2090057,
        "New Delhi, India",
        "astrosage",
        "Ascendant, Moon, Hasta pada 4, and Vimshottari sequence verified against AstroSage.",
    ),
    ChartSeed("delhi_1990_1030", "Delhi Native 1990", date(1990, 1, 15), time(10, 30), "Asia/Kolkata", 28.6139, 77.2090, "New Delhi, India", "engine_locked"),
    ChartSeed("mumbai_1985_0630", "Mumbai Native 1985", date(1985, 3, 22), time(6, 30), "Asia/Kolkata", 19.0760, 72.8777, "Mumbai, India", "engine_locked"),
    ChartSeed("chennai_1992_2145", "Chennai Native 1992", date(1992, 11, 8), time(21, 45), "Asia/Kolkata", 13.0827, 80.2707, "Chennai, India", "engine_locked"),
    ChartSeed("kolkata_1978_1200", "Kolkata Native 1978", date(1978, 7, 4), time(12, 0), "Asia/Kolkata", 22.5726, 88.3639, "Kolkata, India", "engine_locked"),
    ChartSeed("bangalore_2000_0000", "Bangalore Native 2000", date(2000, 1, 1), time(0, 0), "Asia/Kolkata", 12.9716, 77.5946, "Bangalore, India", "engine_locked"),
    ChartSeed("hyderabad_1988_1430", "Hyderabad Native 1988", date(1988, 5, 17), time(14, 30), "Asia/Kolkata", 17.3850, 78.4867, "Hyderabad, India", "engine_locked"),
    ChartSeed("pune_1995_0815", "Pune Native 1995", date(1995, 9, 3), time(8, 15), "Asia/Kolkata", 18.5204, 73.8567, "Pune, India", "engine_locked"),
    ChartSeed("ahmedabad_1970_1800", "Ahmedabad Native 1970", date(1970, 12, 25), time(18, 0), "Asia/Kolkata", 23.0225, 72.5714, "Ahmedabad, India", "engine_locked"),
    ChartSeed("jaipur_2005_1100", "Jaipur Native 2005", date(2005, 4, 10), time(11, 0), "Asia/Kolkata", 26.9124, 75.7873, "Jaipur, India", "engine_locked"),
    ChartSeed("lucknow_1983_0500", "Lucknow Native 1983", date(1983, 2, 14), time(5, 0), "Asia/Kolkata", 26.8467, 80.9462, "Lucknow, India", "engine_locked"),
    ChartSeed("chandigarh_1998_1630", "Chandigarh Native 1998", date(1998, 8, 20), time(16, 30), "Asia/Kolkata", 30.7333, 76.7794, "Chandigarh, India", "engine_locked"),
    ChartSeed("kochi_1975_0200", "Kochi Native 1975", date(1975, 6, 30), time(2, 0), "Asia/Kolkata", 9.9312, 76.2673, "Kochi, India", "engine_locked"),
    ChartSeed("bhopal_1991_0700", "Bhopal Native 1991", date(1991, 10, 12), time(7, 0), "Asia/Kolkata", 23.2599, 77.4126, "Bhopal, India", "engine_locked"),
    ChartSeed("noida_2010_1220", "Noida Native 2010", date(2010, 3, 5), time(12, 20), "Asia/Kolkata", 28.5355, 77.3910, "Noida, India", "engine_locked"),
    ChartSeed("varanasi_1965_2345", "Varanasi Native 1965", date(1965, 4, 18), time(23, 45), "Asia/Kolkata", 25.3176, 82.9739, "Varanasi, India", "engine_locked"),
    ChartSeed("london_1986_0900", "London Native 1986", date(1986, 6, 12), time(9, 0), "Europe/London", 51.5074, -0.1278, "London, UK", "engine_locked"),
    ChartSeed("new_york_1999_1700", "New York Native 1999", date(1999, 12, 31), time(17, 0), "America/New_York", 40.7128, -74.0060, "New York, USA", "engine_locked"),
    ChartSeed("sydney_1980_0600", "Sydney Native 1980", date(1980, 2, 29), time(6, 0), "Australia/Sydney", -33.8688, 151.2093, "Sydney, Australia", "engine_locked"),
    ChartSeed("dubai_1993_1200", "Dubai Native 1993", date(1993, 7, 21), time(12, 0), "Asia/Dubai", 25.2048, 55.2708, "Dubai, UAE", "engine_locked"),
    ChartSeed("singapore_1972_1500", "Singapore Native 1972", date(1972, 9, 9), time(15, 0), "Asia/Singapore", 1.3521, 103.8198, "Singapore", "engine_locked"),
    ChartSeed("tokyo_1989_0800", "Tokyo Native 1989", date(1989, 1, 7), time(8, 0), "Asia/Tokyo", 35.6762, 139.6503, "Tokyo, Japan", "engine_locked"),
    ChartSeed("moscow_1977_1400", "Moscow Native 1977", date(1977, 11, 23), time(14, 0), "Europe/Moscow", 55.7558, 37.6173, "Moscow, Russia", "engine_locked"),
)


def _serialize_planet(planet: Any) -> dict[str, Any]:
    return {
        "longitude": round(planet.longitude, 8),
        "sign": planet.sign.name_en,
        "degree_in_sign": round(planet.sign.degree_in_sign, 8),
        "house": planet.house,
        "nakshatra": planet.nakshatra.name,
        "pada": planet.nakshatra.pada,
        "is_retrograde": planet.is_retrograde,
    }


def _serialize_ascendant(ascendant: Any) -> dict[str, Any]:
    return {
        "longitude": round(ascendant.longitude, 8),
        "sign": ascendant.sign.name_en,
        "degree_in_sign": round(ascendant.sign.degree_in_sign, 8),
        "nakshatra": ascendant.nakshatra.name,
        "pada": ascendant.nakshatra.pada,
    }


def _serialize_dasha_period(period: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "lord": period["lord"],
        "start": period["start"],
        "end": period["end"],
    }
    if period.get("antardashas"):
        payload["antardashas"] = [_serialize_dasha_period(ad) for ad in period["antardashas"]]
    return payload


def build_expected_payload(seed: ChartSeed, engine: VedicAstrologyEngine) -> dict[str, Any]:
    birth_data = build_birth_data(
        date_of_birth=seed.date_of_birth,
        birth_time=seed.birth_time,
        latitude=seed.latitude,
        longitude=seed.longitude,
        timezone_name=seed.timezone,
    )
    bundle = engine.compute_chart(birth_data)
    dasha_input = build_dasha_input_from_bundle(bundle, birth_place=seed.place, timezone=seed.timezone)
    dasha_result = engine.compute_vimshottari_dasha(dasha_input, reference_datetime=DASHA_REFERENCE)
    dasha_payload = to_json_dict(dasha_result)

    planets = {planet.name: _serialize_planet(planet) for planet in bundle.lagna_kundali.planets}
    mahadashas = [_serialize_dasha_period(md) for md in dasha_payload["mahadashas"]]

    return {
        "datetime_utc": bundle.metadata.datetime_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "julian_day": round(bundle.metadata.julian_day, 8),
        "ascendant": _serialize_ascendant(bundle.lagna_kundali.ascendant),
        "planets": planets,
        "dasha": {
            "reference_datetime": DASHA_REFERENCE.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "balance_lord": dasha_payload["balance"]["lord"],
            "mahadashas": mahadashas,
            "current": {
                "mahadasha": dasha_payload["current"]["mahadasha"]["lord"],
                "antardasha": dasha_payload["current"]["antardasha"]["lord"],
            },
        },
    }


def build_chart_file(seed: ChartSeed, engine: VedicAstrologyEngine) -> dict[str, Any]:
    return {
        "id": seed.chart_id,
        "name": seed.name,
        "source": seed.source,
        "notes": seed.notes,
        "reference_settings": {
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "node": "mean",
            "reference_software": "AstroSage/JHora compatible (Lahiri, whole sign, mean node)",
        },
        "birth": {
            "date": seed.date_of_birth.isoformat(),
            "time": seed.birth_time.replace(microsecond=0).isoformat(),
            "timezone": seed.timezone,
            "latitude": seed.latitude,
            "longitude": seed.longitude,
            "place": seed.place,
        },
        "expected": build_expected_payload(seed, engine),
    }


def write_golden_dataset() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    engine = VedicAstrologyEngine()
    manifest_charts = []

    for seed in CHART_SEEDS:
        chart_payload = build_chart_file(seed, engine)
        chart_path = CHARTS_DIR / f"{seed.chart_id}.json"
        with chart_path.open("w", encoding="utf-8") as handle:
            json.dump(chart_payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        manifest_charts.append(
            {
                "id": seed.chart_id,
                "name": seed.name,
                "file": f"charts/{seed.chart_id}.json",
                "source": seed.source,
            }
        )

    manifest = {
        "version": 1,
        "description": "Golden chart dataset for astrology engine accuracy lockdown (Phase 16).",
        "tolerances": {
            "longitude_degrees": 0.01,
            "ascendant_degrees": 0.01,
            "dasha_dates": "exact",
        },
        "reference_settings": {
            "ayanamsa": "lahiri",
            "house_system": "whole_sign",
            "node": "mean",
        },
        "charts": manifest_charts,
    }
    with (GOLDEN_DIR / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Wrote {len(manifest_charts)} golden charts to {GOLDEN_DIR}")


if __name__ == "__main__":
    write_golden_dataset()
