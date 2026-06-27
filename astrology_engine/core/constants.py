"""Vedic astrology constants for Swiss Ephemeris calculations."""

from __future__ import annotations

# Swiss Ephemeris body identifiers (SE_* constants)
SE_SUN = 0
SE_MOON = 1
SE_MERCURY = 2
SE_VENUS = 3
SE_MARS = 4
SE_JUPITER = 5
SE_SATURN = 6
SE_MEAN_NODE = 10
SE_TRUE_NODE = 11

# Swiss Ephemeris sidereal mode identifiers
SE_SIDM_LAHIRI = 1
SE_SIDM_RAMAN = 3
SE_SIDM_KRISHNAMURTI = 5
SE_SIDM_YUKTESHWAR = 7

# Swiss Ephemeris calculation flags
SEFLG_SWIEPH = 2
SEFLG_SPEED = 256
SEFLG_SIDEREAL = 64 * 1024

PLANET_IDS: dict[str, int] = {
    "Sun": SE_SUN,
    "Moon": SE_MOON,
    "Mars": SE_MARS,
    "Mercury": SE_MERCURY,
    "Jupiter": SE_JUPITER,
    "Venus": SE_VENUS,
    "Saturn": SE_SATURN,
    "Rahu": SE_MEAN_NODE,
}

PLANET_ORDER: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

SIGN_NAMES_EN: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SIGN_NAMES_SA: tuple[str, ...] = (
    "Mesha",
    "Vrishabha",
    "Mithuna",
    "Karka",
    "Simha",
    "Kanya",
    "Tula",
    "Vrishchika",
    "Dhanu",
    "Makara",
    "Kumbha",
    "Meena",
)

SIGN_LORDS: tuple[str, ...] = (
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
)

NAKSHATRA_NAMES: tuple[str, ...] = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

NAKSHATRA_LORDS: tuple[str, ...] = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
) * 3

HOUSE_SYSTEM_WHOLE_SIGN = b"W"
HOUSE_SYSTEM_EQUAL = b"E"
HOUSE_SYSTEM_PLACIDUS = b"P"
HOUSE_SYSTEM_SRIPATHI = b"S"

DEFAULT_AYANAMSA = SE_SIDM_LAHIRI

DEGREES_PER_SIGN = 30.0
DEGREES_PER_NAKSHATRA = 360.0 / 27.0
DEGREES_PER_NAVAMSHA = 30.0 / 9.0
NUM_SIGNS = 12
NUM_HOUSES = 12
