"""Evidence providers extracting signals from existing engine outputs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from backend.app.services.consultation_brain.constants import SOURCE_WEIGHTS, EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationInput


def _safe_float(value: Any, *, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if parsed < 0.0:
        return 0.0
    if parsed > 1.0:
        return 1.0
    return parsed


def _safe_str(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _section(report: Mapping[str, Any], key: str) -> dict[str, Any] | None:
    value = report.get(key)
    return value if isinstance(value, dict) else None


def _join_labels(values: Sequence[Any]) -> str:
    return ", ".join(_safe_str(item) for item in values if _safe_str(item))


class BaseSubsystemEvidenceProvider(ABC):
    """Base class for stateless subsystem evidence extractors."""

    @property
    @abstractmethod
    def source(self) -> EvidenceSource:
        """Evidence source handled by this provider."""

    @property
    def default_category(self) -> EvidenceCategory:
        if self.source in {EvidenceSource.DASHA, EvidenceSource.TRANSIT}:
            return EvidenceCategory.TIMING
        if self.source in {EvidenceSource.LAL_KITAB, EvidenceSource.RULE_STUDIO}:
            return EvidenceCategory.REMEDY
        if self.source == EvidenceSource.PROFESSIONAL_REPORT:
            return EvidenceCategory.GENERAL
        return EvidenceCategory.GENERAL

    @property
    def default_weight(self) -> float:
        return float(SOURCE_WEIGHTS.get(self.source, 0.5))

    def _build_evidence(
        self,
        *,
        evidence_id: str,
        title: str,
        summary: str,
        confidence: float,
        raw_reference: str,
        category: EvidenceCategory | None = None,
        tags: Sequence[str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ConsultationEvidence:
        normalized_tags = tuple(
            sorted({_safe_str(tag).lower() for tag in (tags or (self.source.value,)) if _safe_str(tag)})
        )
        return ConsultationEvidence(
            evidence_id=evidence_id,
            source=self.source,
            category=category or self.default_category,
            title=_safe_str(title),
            summary=_safe_str(summary),
            weight=self.default_weight,
            confidence=_safe_float(confidence),
            raw_reference=_safe_str(raw_reference),
            tags=normalized_tags,
            metadata=dict(metadata or {}),
        )

    async def collect_async(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        return self.collect(consultation_input)


class YogaEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.YOGAS

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "yogas")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        for index, yoga in enumerate(section.get("present_yogas") or []):
            if not isinstance(yoga, dict):
                continue
            yoga_id = _safe_str(yoga.get("yoga_id") or yoga.get("name") or f"yoga-{index + 1}")
            planets = _join_labels(yoga.get("planets_involved") or [])
            houses = _join_labels(yoga.get("houses_involved") or [])
            summary_parts = [part for part in (planets and f"Planets: {planets}", houses and f"Houses: {houses}") if part]
            evidence.append(
                self._build_evidence(
                    evidence_id=f"yoga-{yoga_id}",
                    title=yoga.get("name") or yoga_id.replace("_", " ").title(),
                    summary="; ".join(summary_parts) or "Yoga present in chart analysis.",
                    confidence=_safe_float(yoga.get("strength"), default=0.5),
                    raw_reference=f"yogas.present_yogas[{index}]",
                    tags=("yoga", yoga_id),
                    metadata={"yoga_id": yoga_id},
                )
            )
        summary = section.get("summary")
        if isinstance(summary, dict):
            present_count = summary.get("present_count")
            if present_count is not None:
                evidence.append(
                    self._build_evidence(
                        evidence_id="yoga-summary",
                        title="Yoga summary",
                        summary=f"{present_count} yogas identified in report.",
                        confidence=0.4,
                        raw_reference="yogas.summary",
                        tags=("yoga", "summary"),
                        metadata={"present_count": present_count},
                    )
                )
        return tuple(evidence)


class DashaEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.DASHA

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "dasha")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        current = section.get("current")
        if isinstance(current, dict):
            for period_key in ("mahadasha", "antardasha", "pratyantardasha"):
                period = current.get(period_key)
                if not isinstance(period, dict):
                    continue
                lord = _safe_str(period.get("lord") or period.get("planet"))
                if not lord:
                    continue
                evidence.append(
                    self._build_evidence(
                        evidence_id=f"dasha-{period_key}-{lord.lower()}",
                        title=f"Active {period_key.replace('_', ' ')}: {lord}",
                        summary=f"Current {period_key} lord is {lord}.",
                        confidence=_safe_float(period.get("strength"), default=0.55),
                        raw_reference=f"dasha.current.{period_key}",
                        category=EvidenceCategory.TIMING,
                        tags=("dasha", period_key, lord.lower()),
                        metadata={"period": period_key, "lord": lord},
                    )
                )
        system = _safe_str(section.get("system"))
        if system:
            evidence.append(
                self._build_evidence(
                    evidence_id=f"dasha-system-{system.lower()}",
                    title=f"Dasha system: {system}",
                    summary=f"Report uses {system} dasha timeline.",
                    confidence=0.5,
                    raw_reference="dasha.system",
                    category=EvidenceCategory.TIMING,
                    tags=("dasha", "system", system.lower()),
                )
            )
        return tuple(evidence)


class TransitEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.TRANSIT

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "transits")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        for planet_key, payload in sorted(section.items()):
            if planet_key in {"metadata", "highlights", "summary"}:
                continue
            if not isinstance(payload, dict):
                continue
            planet = _safe_str(payload.get("planet") or planet_key).title()
            impacts = payload.get("natal_impacts") or []
            impact_types = [
                _safe_str(item.get("impact_type"))
                for item in impacts
                if isinstance(item, dict) and _safe_str(item.get("impact_type"))
            ]
            current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
            house = current.get("house_from_lagna")
            summary_parts = []
            if impact_types:
                summary_parts.append(f"Impacts: {_join_labels(impact_types)}")
            if house is not None:
                summary_parts.append(f"Current house from lagna: {house}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"transit-{planet_key.lower()}",
                    title=f"{planet} transit",
                    summary="; ".join(summary_parts) or f"{planet} transit data present.",
                    confidence=max(
                        (_safe_float(item.get("strength")) for item in impacts if isinstance(item, dict)),
                        default=0.45,
                    ),
                    raw_reference=f"transits.{planet_key}",
                    category=EvidenceCategory.TIMING,
                    tags=("transit", planet.lower()),
                    metadata={"planet": planet, "impact_types": tuple(impact_types)},
                )
            )
        return tuple(evidence)


class KPEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.KP

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        report = consultation_input.unified_report
        evidence: list[ConsultationEvidence] = []
        kp_analysis = _section(report, "kp_analysis")
        if kp_analysis is not None:
            for index, event in enumerate(kp_analysis.get("events") or []):
                if not isinstance(event, dict):
                    continue
                event_id = _safe_str(event.get("event_id") or event.get("event_type") or f"event-{index + 1}")
                supported = event.get("is_supported")
                evidence.append(
                    self._build_evidence(
                        evidence_id=f"kp-event-{event_id}",
                        title=_safe_str(event.get("event_type") or event_id).replace("_", " ").title(),
                        summary=(
                            f"Support score {_safe_float(event.get('support_score')):.2f}; "
                            f"supported={supported}"
                        ),
                        confidence=_safe_float(event.get("support_score"), default=0.4),
                        raw_reference=f"kp_analysis.events[{index}]",
                        tags=("kp", "event", event_id),
                        metadata={"event_id": event_id, "is_supported": supported},
                    )
                )
            summary = kp_analysis.get("summary")
            if isinstance(summary, dict):
                supported_events = summary.get("supported_events")
                total_events = summary.get("total_events")
                if supported_events is not None and total_events is not None:
                    evidence.append(
                        self._build_evidence(
                            evidence_id="kp-summary",
                            title="KP event summary",
                            summary=f"{supported_events}/{total_events} KP events supported.",
                            confidence=_safe_float(supported_events) / max(float(total_events), 1.0),
                            raw_reference="kp_analysis.summary",
                            tags=("kp", "summary"),
                        )
                    )
        kp_intel = _section(report, "kp")
        if kp_intel is not None:
            for index, observation in enumerate(kp_intel.get("observations") or []):
                if not isinstance(observation, dict):
                    continue
                obs_id = _safe_str(observation.get("observation_id") or f"obs-{index + 1}")
                evidence.append(
                    self._build_evidence(
                        evidence_id=f"kp-observation-{obs_id}",
                        title=_safe_str(observation.get("title") or obs_id),
                        summary=_safe_str(observation.get("summary") or observation.get("text") or "KP observation."),
                        confidence=_safe_float(observation.get("confidence"), default=0.45),
                        raw_reference=f"kp.observations[{index}]",
                        tags=("kp", "observation", obs_id),
                    )
                )
        return tuple(evidence)


class LalKitabEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.LAL_KITAB

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        report = consultation_input.unified_report
        evidence: list[ConsultationEvidence] = []
        section = _section(report, "lal_kitab")
        if section is not None:
            for collection_key, tag in (("dosh_findings", "dosh"), ("rin_findings", "rin")):
                for index, finding in enumerate(section.get(collection_key) or []):
                    if not isinstance(finding, dict):
                        continue
                    finding_id = _safe_str(
                        finding.get("finding_id") or finding.get("finding_name") or f"{tag}-{index + 1}"
                    )
                    if finding.get("is_present") is False:
                        continue
                    evidence.append(
                        self._build_evidence(
                            evidence_id=f"lal-kitab-{tag}-{finding_id}",
                            title=_safe_str(finding.get("finding_name") or finding_id),
                            summary=f"Lal Kitab {tag} finding with strength "
                            f"{_safe_float(finding.get('strength'), default=0.5):.2f}.",
                            confidence=_safe_float(finding.get("strength"), default=0.5),
                            raw_reference=f"lal_kitab.{collection_key}[{index}]",
                            category=EvidenceCategory.REMEDY,
                            tags=("lal_kitab", tag, finding_id),
                        )
                    )
        lk_intel = _section(report, "lal_kitab_intelligence")
        if lk_intel is not None:
            for index, observation in enumerate(lk_intel.get("observations") or []):
                if not isinstance(observation, dict):
                    continue
                obs_id = _safe_str(observation.get("observation_id") or f"lk-{index + 1}")
                evidence.append(
                    self._build_evidence(
                        evidence_id=f"lal-kitab-intel-{obs_id}",
                        title=_safe_str(observation.get("title") or obs_id),
                        summary=_safe_str(observation.get("summary") or "Lal Kitab intelligence observation."),
                        confidence=_safe_float(observation.get("confidence"), default=0.45),
                        raw_reference=f"lal_kitab_intelligence.observations[{index}]",
                        category=EvidenceCategory.REMEDY,
                        tags=("lal_kitab", "intelligence", obs_id),
                    )
                )
        return tuple(evidence)


class RuleStudioEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.RULE_STUDIO

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "rule_studio")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        rules = section.get("matched_rules") or section.get("rules") or section.get("active_rules") or []
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue
            rule_id = _safe_str(rule.get("rule_id") or rule.get("id") or f"rule-{index + 1}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"rule-studio-{rule_id}",
                    title=_safe_str(rule.get("title") or rule.get("name") or rule_id),
                    summary=_safe_str(rule.get("summary") or rule.get("description") or "Rule studio match."),
                    confidence=_safe_float(rule.get("confidence") or rule.get("match_score"), default=0.5),
                    raw_reference=f"rule_studio.rules[{index}]",
                    category=EvidenceCategory.REMEDY,
                    tags=("rule_studio", rule_id),
                    metadata={"rule_id": rule_id, "domain": rule.get("domain")},
                )
            )
        return tuple(evidence)


class CaseLearningEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.CASE_LEARNING

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "case_learning")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        patterns = section.get("matched_patterns") or section.get("patterns") or section.get("cases") or []
        for index, pattern in enumerate(patterns):
            if not isinstance(pattern, dict):
                continue
            pattern_id = _safe_str(pattern.get("pattern_id") or pattern.get("case_id") or f"pattern-{index + 1}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"case-learning-{pattern_id}",
                    title=_safe_str(pattern.get("title") or pattern.get("category") or pattern_id),
                    summary=_safe_str(pattern.get("summary") or pattern.get("outcome") or "Similar case pattern."),
                    confidence=_safe_float(pattern.get("similarity") or pattern.get("confidence"), default=0.5),
                    raw_reference=f"case_learning.patterns[{index}]",
                    tags=("case_learning", pattern_id),
                    metadata={"pattern_id": pattern_id},
                )
            )
        return tuple(evidence)


class FusionEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.FUSION

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "fusion")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        confidence = section.get("confidence")
        if confidence is not None:
            evidence.append(
                self._build_evidence(
                    evidence_id="fusion-confidence",
                    title="Fusion confidence",
                    summary=f"Intelligence fusion confidence {_safe_float(confidence):.2f}.",
                    confidence=_safe_float(confidence),
                    raw_reference="fusion.confidence",
                    tags=("fusion", "confidence"),
                )
            )
        for index, root_cause in enumerate(section.get("root_causes") or []):
            if not isinstance(root_cause, dict):
                continue
            cause_id = _safe_str(root_cause.get("cause_id") or root_cause.get("label") or f"cause-{index + 1}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"fusion-root-{cause_id}",
                    title=_safe_str(root_cause.get("label") or cause_id),
                    summary=_safe_str(root_cause.get("summary") or root_cause.get("description") or "Fusion root cause."),
                    confidence=_safe_float(root_cause.get("confidence"), default=0.6),
                    raw_reference=f"fusion.root_causes[{index}]",
                    tags=("fusion", "root_cause", cause_id),
                )
            )
        for index, observation in enumerate(section.get("observations") or []):
            if not isinstance(observation, dict):
                continue
            obs_id = _safe_str(observation.get("observation_id") or f"fusion-obs-{index + 1}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"fusion-observation-{obs_id}",
                    title=_safe_str(observation.get("title") or obs_id),
                    summary=_safe_str(observation.get("summary") or "Fusion observation."),
                    confidence=_safe_float(observation.get("confidence"), default=0.55),
                    raw_reference=f"fusion.observations[{index}]",
                    tags=("fusion", "observation", obs_id),
                )
            )
        return tuple(evidence)


class GoldenDatasetEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.GOLDEN_DATASET

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        section = _section(consultation_input.unified_report, "golden_dataset")
        if section is None:
            return ()
        evidence: list[ConsultationEvidence] = []
        matches = section.get("matches") or section.get("benchmark_matches") or section.get("cases") or []
        for index, match in enumerate(matches):
            if not isinstance(match, dict):
                continue
            match_id = _safe_str(match.get("match_id") or match.get("case_id") or f"match-{index + 1}")
            evidence.append(
                self._build_evidence(
                    evidence_id=f"golden-dataset-{match_id}",
                    title=_safe_str(match.get("title") or match.get("category") or match_id),
                    summary=_safe_str(match.get("summary") or match.get("expected_outcome") or "Golden dataset match."),
                    confidence=_safe_float(match.get("match_score") or match.get("similarity"), default=0.55),
                    raw_reference=f"golden_dataset.matches[{index}]",
                    tags=("golden_dataset", match_id),
                    metadata={"match_id": match_id},
                )
            )
        return tuple(evidence)


class ProfessionalReportEvidenceProvider(BaseSubsystemEvidenceProvider):
    @property
    def source(self) -> EvidenceSource:
        return EvidenceSource.PROFESSIONAL_REPORT

    def collect(self, consultation_input: ConsultationInput) -> tuple[ConsultationEvidence, ...]:
        report = consultation_input.professional_report
        if not isinstance(report, dict):
            return ()
        evidence: list[ConsultationEvidence] = []
        sections = report.get("sections") or []
        for index, section in enumerate(sections):
            if not isinstance(section, dict):
                continue
            section_id = _safe_str(section.get("section_id") or section.get("id") or section.get("type") or f"section-{index + 1}")
            facts = section.get("facts") or section.get("key_points") or []
            fact_lines = [_safe_str(fact) for fact in facts if _safe_str(fact)]
            evidence.append(
                self._build_evidence(
                    evidence_id=f"professional-report-{section_id}",
                    title=_safe_str(section.get("title") or section.get("heading") or section_id),
                    summary=" ".join(fact_lines[:3]) or _safe_str(section.get("summary") or "Professional report section."),
                    confidence=_safe_float(section.get("confidence"), default=0.6),
                    raw_reference=f"professional_report.sections[{index}]",
                    tags=("professional_report", section_id),
                    metadata={"section_id": section_id, "fact_count": len(fact_lines)},
                )
            )
        return tuple(evidence)


def default_collection_providers() -> tuple[BaseSubsystemEvidenceProvider, ...]:
    """Return a fresh provider set for the evidence collection engine."""
    return (
        YogaEvidenceProvider(),
        DashaEvidenceProvider(),
        TransitEvidenceProvider(),
        KPEvidenceProvider(),
        LalKitabEvidenceProvider(),
        RuleStudioEvidenceProvider(),
        CaseLearningEvidenceProvider(),
        FusionEvidenceProvider(),
        GoldenDatasetEvidenceProvider(),
        ProfessionalReportEvidenceProvider(),
    )


# Backward-compatible alias used by earlier foundation wiring.
default_evidence_providers = default_collection_providers
