"""Domain analyzers that transform structured inputs into analysis artifacts."""

from __future__ import annotations

from backend.app.services.reasoning.models import (
    AnalysisBundle,
    BirthDetailsInput,
    DashaInput,
    DomainAnalysis,
    Evidence,
    HousesInput,
    KPDataInput,
    LalKitabDataInput,
    Observation,
    PlanetPositionsInput,
    ReasoningEngineInput,
    TransitInput,
)
from backend.app.services.reasoning.types import DOMAIN_WEIGHTS, EvidenceKind, ReasoningDomain


class ReasoningAnalyzer:
    """
    Produces domain-scoped analysis artifacts from structured horoscope inputs.

    This class defines the analysis pipeline contract. Interpretive astrology
    rules are intentionally omitted; only structural coverage observations and
    evidence records are emitted so downstream modules can attach logic later.
    """

    def analyze(self, reasoning_input: ReasoningEngineInput) -> AnalysisBundle:
        """Run all domain analyzers and return a combined analysis bundle."""
        analyses = (
            self.analyze_birth_details(reasoning_input.birth_details),
            self.analyze_planet_positions(reasoning_input.planet_positions),
            self.analyze_houses(reasoning_input.houses),
            self.analyze_dasha(reasoning_input.dasha),
            self.analyze_transit(reasoning_input.transit),
            self.analyze_kp_data(reasoning_input.kp_data),
            self.analyze_lal_kitab_data(reasoning_input.lal_kitab_data),
        )
        return AnalysisBundle(domain_analyses=analyses)

    def analyze_birth_details(self, birth_details: BirthDetailsInput) -> DomainAnalysis:
        """Build structural observations for the birth profile domain."""
        observation = Observation(
            observation_id=f"{ReasoningDomain.BIRTH_DETAILS.value}-profile",
            domain=ReasoningDomain.BIRTH_DETAILS,
            summary=(
                f"Birth profile loaded for {birth_details.birth_place} "
                f"on {birth_details.date_of_birth.isoformat()}."
            ),
            source="birth_details",
            details={
                "birth_time": birth_details.birth_time.isoformat(),
                "timezone": birth_details.timezone,
                "latitude": birth_details.latitude,
                "longitude": birth_details.longitude,
                "person_name": birth_details.person_name,
                "client_id": birth_details.client_id,
            },
        )
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.BIRTH_DETAILS.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.BIRTH_DETAILS,
                statement="Birth details input is complete and available for reasoning.",
                source="birth_details",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.BIRTH_DETAILS],
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.BIRTH_DETAILS,
            observations=(observation,),
            evidence=evidence,
            coverage_score=1.0,
        )

    def analyze_planet_positions(
        self,
        planet_positions: PlanetPositionsInput,
    ) -> DomainAnalysis:
        """Build structural observations for planetary position data."""
        planet_count = len(planet_positions.planets)
        observation = Observation(
            observation_id=f"{ReasoningDomain.PLANET_POSITIONS.value}-positions",
            domain=ReasoningDomain.PLANET_POSITIONS,
            summary=f"Loaded {planet_count} planetary position records.",
            source="planet_positions",
            details={
                "planet_count": planet_count,
                "ascendant_sign": planet_positions.ascendant_sign,
                "moon_sign": planet_positions.moon_sign,
                "planets": tuple(
                    {
                        "name": planet.name,
                        "sign": planet.sign,
                        "house": planet.house,
                        "longitude": planet.longitude,
                        "nakshatra": planet.nakshatra,
                        "is_retrograde": planet.is_retrograde,
                    }
                    for planet in planet_positions.planets
                ),
            },
        )
        coverage_score = 1.0 if planet_count > 0 else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.PLANET_POSITIONS.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.PLANET_POSITIONS,
                statement=(
                    "Planetary position data is present."
                    if planet_count
                    else "Planetary position data is missing."
                ),
                source="planet_positions",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.PLANET_POSITIONS] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.PLANET_POSITIONS,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    def analyze_houses(self, houses: HousesInput) -> DomainAnalysis:
        """Build structural observations for house map data."""
        house_count = len(houses.cusps)
        observation = Observation(
            observation_id=f"{ReasoningDomain.HOUSES.value}-map",
            domain=ReasoningDomain.HOUSES,
            summary=f"Loaded {house_count} house records.",
            source="houses",
            details={
                "house_count": house_count,
                "ascendant_sign": houses.ascendant_sign,
                "house_system": houses.house_system,
                "cusps": tuple(
                    {
                        "number": cusp.number,
                        "sign": cusp.sign,
                        "longitude": cusp.longitude,
                    }
                    for cusp in houses.cusps
                ),
            },
        )
        coverage_score = 1.0 if house_count > 0 else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.HOUSES.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.HOUSES,
                statement=(
                    "House map data is present."
                    if house_count
                    else "House map data is missing."
                ),
                source="houses",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.HOUSES] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.HOUSES,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    def analyze_dasha(self, dasha: DashaInput) -> DomainAnalysis:
        """Build structural observations for dasha timeline data."""
        period_count = len(dasha.mahadashas)
        active_levels = tuple(
            level
            for level, period in (
                ("mahadasha", dasha.current_mahadasha),
                ("antardasha", dasha.current_antardasha),
                ("pratyantar", dasha.current_pratyantar),
            )
            if period is not None
        )
        observation = Observation(
            observation_id=f"{ReasoningDomain.DASHA.value}-timeline",
            domain=ReasoningDomain.DASHA,
            summary=(
                f"Loaded dasha system '{dasha.system}' with "
                f"{period_count} mahadasha records."
            ),
            source="dasha",
            details={
                "system": dasha.system,
                "mahadasha_count": period_count,
                "active_levels": active_levels,
                "metadata": dasha.metadata,
            },
        )
        coverage_score = 1.0 if period_count or active_levels else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.DASHA.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.DASHA,
                statement=(
                    "Dasha timeline data is present."
                    if coverage_score
                    else "Dasha timeline data is missing."
                ),
                source="dasha",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.DASHA] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.DASHA,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    def analyze_transit(self, transit: TransitInput) -> DomainAnalysis:
        """Build structural observations for transit snapshot data."""
        transit_count = len(transit.planets)
        observation = Observation(
            observation_id=f"{ReasoningDomain.TRANSIT.value}-snapshot",
            domain=ReasoningDomain.TRANSIT,
            summary=f"Loaded {transit_count} transit planet records.",
            source="transit",
            details={
                "reference_datetime": (
                    transit.reference_datetime.isoformat()
                    if transit.reference_datetime is not None
                    else None
                ),
                "transit_count": transit_count,
                "metadata": transit.metadata,
            },
        )
        coverage_score = 1.0 if transit_count > 0 else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.TRANSIT.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.TRANSIT,
                statement=(
                    "Transit data is present."
                    if transit_count
                    else "Transit data is missing."
                ),
                source="transit",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.TRANSIT] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.TRANSIT,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    def analyze_kp_data(self, kp_data: KPDataInput) -> DomainAnalysis:
        """Build structural observations for KP analysis data."""
        cusp_count = len(kp_data.cusps)
        significator_count = len(kp_data.significators)
        observation = Observation(
            observation_id=f"{ReasoningDomain.KP.value}-analysis",
            domain=ReasoningDomain.KP,
            summary=(
                f"Loaded KP data with {cusp_count} cusps and "
                f"{significator_count} significator sets."
            ),
            source="kp_data",
            details={
                "lagna_sign": kp_data.lagna_sign,
                "cusp_count": cusp_count,
                "significator_count": significator_count,
                "supported_events": kp_data.supported_events,
                "metadata": kp_data.metadata,
            },
        )
        coverage_score = 1.0 if cusp_count or significator_count else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.KP.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.KP,
                statement=(
                    "KP analysis data is present."
                    if coverage_score
                    else "KP analysis data is missing."
                ),
                source="kp_data",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.KP] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.KP,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    def analyze_lal_kitab_data(self, lal_kitab_data: LalKitabDataInput) -> DomainAnalysis:
        """Build structural observations for Lal Kitab analysis data."""
        finding_count = len(lal_kitab_data.findings)
        present_count = sum(1 for finding in lal_kitab_data.findings if finding.is_present)
        observation = Observation(
            observation_id=f"{ReasoningDomain.LAL_KITAB.value}-analysis",
            domain=ReasoningDomain.LAL_KITAB,
            summary=(
                f"Loaded {finding_count} Lal Kitab findings "
                f"({present_count} marked present)."
            ),
            source="lal_kitab_data",
            details={
                "lagna_sign": lal_kitab_data.lagna_sign,
                "finding_count": finding_count,
                "present_count": present_count,
                "metadata": lal_kitab_data.metadata,
            },
        )
        coverage_score = 1.0 if finding_count > 0 else 0.0
        evidence = (
            Evidence(
                evidence_id=f"{ReasoningDomain.LAL_KITAB.value}-coverage",
                kind=EvidenceKind.COVERAGE,
                domain=ReasoningDomain.LAL_KITAB,
                statement=(
                    "Lal Kitab analysis data is present."
                    if finding_count
                    else "Lal Kitab analysis data is missing."
                ),
                source="lal_kitab_data",
                reference_id=observation.observation_id,
                weight=DOMAIN_WEIGHTS[ReasoningDomain.LAL_KITAB] * coverage_score,
            ),
        )
        return self._build_domain_analysis(
            domain=ReasoningDomain.LAL_KITAB,
            observations=(observation,),
            evidence=evidence,
            coverage_score=coverage_score,
        )

    @staticmethod
    def _build_domain_analysis(
        *,
        domain: ReasoningDomain,
        observations: tuple[Observation, ...],
        evidence: tuple[Evidence, ...],
        coverage_score: float,
    ) -> DomainAnalysis:
        """Create a domain analysis artifact with empty interpretive sections."""
        return DomainAnalysis(
            domain=domain,
            observations=observations,
            detected_patterns=(),
            strengths=(),
            weaknesses=(),
            root_causes=(),
            evidence=evidence,
            recommendations=(),
            coverage_score=coverage_score,
        )
