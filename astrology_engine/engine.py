"""Main Vedic astrology engine orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from astrology_engine.calculations.ascendant import calculate_ascendant
from astrology_engine.calculations.ephemeris import EphemerisConfig, EphemerisService
from astrology_engine.calculations.planets import calculate_planetary_positions
from astrology_engine.charts.bhava_chart import build_bhava_chart
from astrology_engine.charts.lagna_kundali import build_lagna_kundali
from astrology_engine.charts.navamsha import build_navamsha_chart
from astrology_engine.core.base import AstrologyEngine, BirthData
from astrology_engine.dasha.constants import DEFAULT_MAX_YEARS
from astrology_engine.dasha.engine import VimshottariDashaEngine
from astrology_engine.dasha.types import DashaBirthInput, VimshottariDashaResult
from astrology_engine.doshas import DoshaDetectionEngine, DoshaDetectionResult
from astrology_engine.transits import TransitEngine
from astrology_engine.transits.types import TransitAnalysisResult
from astrology_engine.yogas import YogaDetectionEngine, YogaDetectionResult
from astrology_engine.core.types import (
    AyanamsaType,
    BhavaChart,
    ChartMetadata,
    HouseSystemType,
    LagnaKundali,
    NavamshaChart,
    PlanetPosition,
    VedicChartBundle,
)
from astrology_engine.utilities.datetime_utils import ensure_utc


@dataclass(frozen=True)
class EngineInput:
    """Normalized input for astrology engine computations."""

    datetime_utc: datetime
    latitude: float
    longitude: float
    timezone: str

    @classmethod
    def from_birth_data(cls, birth_data: BirthData) -> EngineInput:
        return cls(
            datetime_utc=ensure_utc(birth_data.datetime_utc),
            latitude=birth_data.latitude,
            longitude=birth_data.longitude,
            timezone=birth_data.timezone,
        )


class VedicAstrologyEngine(AstrologyEngine):
    """
    Swiss Ephemeris powered Vedic astrology computation engine.

    Produces planetary positions, lagna kundali (D1), bhava chart, and navamsha (D9).
    """

    def __init__(self, config: EphemerisConfig | None = None) -> None:
        self._config = config or EphemerisConfig()
        self._ephemeris = EphemerisService(self._config)

    @property
    def config(self) -> EphemerisConfig:
        return self._config

    def compute_chart(self, birth_data: BirthData) -> VedicChartBundle:
        """Compute the full Vedic chart bundle for a birth moment."""
        engine_input = EngineInput.from_birth_data(birth_data)
        return self.compute_bundle(
            engine_input.datetime_utc,
            engine_input.latitude,
            engine_input.longitude,
        )

    def compute_bundle(
        self,
        datetime_utc: datetime,
        latitude: float,
        longitude: float,
    ) -> VedicChartBundle:
        """Compute all primary charts and planetary positions."""
        utc_dt = ensure_utc(datetime_utc)
        julian_day = self._ephemeris.get_julian_day(utc_dt)

        ascendant = calculate_ascendant(
            self._ephemeris,
            julian_day,
            latitude,
            longitude,
            house_system=HouseSystemType.WHOLE_SIGN,
        )
        planets = calculate_planetary_positions(self._ephemeris, julian_day)
        lagna_kundali = build_lagna_kundali(ascendant, planets)
        bhava_chart = build_bhava_chart(
            self._ephemeris,
            julian_day,
            latitude,
            longitude,
            ascendant,
            planets,
        )
        navamsha_chart = build_navamsha_chart(ascendant, planets)

        metadata = ChartMetadata(
            julian_day=julian_day,
            ayanamsa=self._config.ayanamsa.value,
            house_system=self._config.house_system.value,
            latitude=latitude,
            longitude=longitude,
            datetime_utc=utc_dt,
        )

        return VedicChartBundle(
            metadata=metadata,
            planetary_positions=lagna_kundali.planets,
            lagna_kundali=lagna_kundali,
            bhava_chart=bhava_chart,
            navamsha_chart=navamsha_chart,
        )

    def compute_planetary_positions(
        self,
        datetime_utc: datetime,
    ) -> tuple[PlanetPosition, ...]:
        """Compute sidereal planetary positions only."""
        julian_day = self._ephemeris.get_julian_day(ensure_utc(datetime_utc))
        return calculate_planetary_positions(self._ephemeris, julian_day)

    def compute_lagna_kundali(
        self,
        datetime_utc: datetime,
        latitude: float,
        longitude: float,
    ) -> LagnaKundali:
        """Compute D1 lagna kundali only."""
        return self.compute_bundle(datetime_utc, latitude, longitude).lagna_kundali

    def compute_bhava_chart(
        self,
        datetime_utc: datetime,
        latitude: float,
        longitude: float,
    ) -> BhavaChart:
        """Compute bhava chart only."""
        return self.compute_bundle(datetime_utc, latitude, longitude).bhava_chart

    def compute_navamsha_chart(
        self,
        datetime_utc: datetime,
        latitude: float,
        longitude: float,
    ) -> NavamshaChart:
        """Compute D9 navamsha chart only."""
        return self.compute_bundle(datetime_utc, latitude, longitude).navamsha_chart

    def compute_vimshottari_dasha(
        self,
        birth_input: DashaBirthInput,
        *,
        reference_datetime: datetime | None = None,
        max_years: float = DEFAULT_MAX_YEARS,
    ) -> VimshottariDashaResult:
        """Compute Vimshottari mahadasha, antardasha, and pratyantar dasha tree."""
        dasha_engine = VimshottariDashaEngine(self._config)
        return dasha_engine.compute(
            birth_input,
            reference_datetime=reference_datetime,
            max_years=max_years,
        )

    def detect_yogas(self, chart_bundle: VedicChartBundle) -> YogaDetectionResult:
        """Detect classical yogas from a computed chart bundle."""
        engine = YogaDetectionEngine()
        return engine.detect(chart_bundle)

    def detect_doshas(self, chart_bundle: VedicChartBundle) -> DoshaDetectionResult:
        """Detect classical doshas from a computed chart bundle."""
        engine = DoshaDetectionEngine()
        return engine.detect(chart_bundle)

    def analyze_transits(
        self,
        chart_bundle: VedicChartBundle,
        *,
        target_date: date | None = None,
        timezone: str | None = None,
    ) -> TransitAnalysisResult:
        """Analyze Saturn, Jupiter, Rahu, and Ketu transits against a natal chart."""
        engine = TransitEngine(self._config)
        return engine.analyze_chart(
            chart_bundle,
            target_date=target_date or date.today(),
            timezone=timezone,
        )
