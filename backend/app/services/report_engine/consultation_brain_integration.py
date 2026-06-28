"""Map ConsultationBrainOutput onto client-facing report section content."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from backend.app.services.consultation_brain.constants import EvidenceSource
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.narrative_models import NarrativeSection, NarrativeSectionId
from backend.app.services.report_engine.language import localize
from backend.app.services.report_engine.presentation import scrub_client_text
from backend.app.services.report_engine.types import ReportLanguage

PLANET_NAMES = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
STRUCTURED_REASON_PATTERN = re.compile(
    r"category=[\w_]+\|domain=[\w_]+\|domain_rank=\d+\|",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BrainReportContext:
    """Client-safe accessors for consultation brain intelligence."""

    output: ConsultationBrainOutput
    language: ReportLanguage

    @property
    def narrative(self):
        return self.output.narrative

    def has_narrative(self) -> bool:
        return self.output.narrative is not None

    def narrative_section(self, section_id: NarrativeSectionId) -> NarrativeSection | None:
        if self.output.narrative is None:
            return None
        for item in self.output.narrative.sections:
            if item.section_id == section_id:
                return item
        return None

    def narrative_paragraphs(self, section_id: NarrativeSectionId) -> tuple[str, ...]:
        section = self.narrative_section(section_id)
        if section is None:
            return ()
        return section.paragraphs

    def narrative_bullets(self, section_id: NarrativeSectionId) -> tuple[str, ...]:
        section = self.narrative_section(section_id)
        if section is None:
            return ()
        return section.bullets

    def narrative_body(self, section_id: NarrativeSectionId) -> str:
        section = self.narrative_section(section_id)
        if section is None:
            return ""
        return scrub_client_text(section.body_text)

    def section_narrative(self, section_id: NarrativeSectionId, *, fallback: str = "") -> str:
        body = self.narrative_body(section_id)
        return body or fallback

    def evidence_for_source(self, source: EvidenceSource) -> tuple[ConsultationEvidence, ...]:
        return tuple(
            item
            for item in sorted(self.output.evidence, key=lambda entry: entry.evidence_id)
            if item.source == source
        )

    def evidence_for_planet(self, planet_name: str) -> tuple[ConsultationEvidence, ...]:
        needle = planet_name.lower()
        matched: list[ConsultationEvidence] = []
        for item in self.output.evidence:
            haystack = f"{item.title} {item.summary} {' '.join(item.tags)}".lower()
            affected = item.metadata.get("affected_planets") or item.metadata.get("planets_involved") or []
            if needle in haystack or any(str(planet).lower() == needle for planet in affected):
                matched.append(item)
        return tuple(matched)

    def priority_lines(self) -> list[str]:
        lines: list[str] = []
        for priority in self.output.priorities[:5]:
            lines.append(self._format_priority(priority))
        return lines

    def recommendation_fact_lines(self) -> list[str]:
        lines: list[str] = []
        for recommendation in self.output.recommendations[:8]:
            lines.append(self._format_recommendation(recommendation))
        return lines

    def conflict_lines(self) -> list[str]:
        lines: list[str] = []
        for conflict in self.output.conflicts[:5]:
            lines.append(self._format_conflict(conflict))
        return lines

    def evidence_summary_lines(self, *, limit: int = 8) -> list[str]:
        lines: list[str] = []
        for item in self.output.evidence[:limit]:
            lines.append(self._format_evidence(item))
        return lines

    def planet_interpretation_lines(self) -> list[str]:
        lines: list[str] = []
        for planet_name in PLANET_NAMES:
            related = self.evidence_for_planet(planet_name)
            if not related:
                continue
            summaries = [self._clean_text(item.summary) for item in related[:2] if item.summary]
            if not summaries:
                continue
            confidence = max(item.confidence for item in related)
            lines.append(
                localize(
                    self.language,
                    hi=(
                        f"{planet_name}: {' '.join(summaries)} "
                        f"(विश्वास {int(round(confidence * 100))}%)"
                    ),
                    en=(
                        f"{planet_name}: {' '.join(summaries)} "
                        f"(confidence {int(round(confidence * 100))}%)"
                    ),
                )
            )
        return lines

    def legacy_remedies(self) -> list[dict[str, Any]]:
        remedies: list[dict[str, Any]] = []
        narrative_bullets = self.narrative_bullets(NarrativeSectionId.RECOMMENDATIONS)
        narrative_bullets += self.narrative_bullets(NarrativeSectionId.PRACTICAL_GUIDANCE)
        if narrative_bullets:
            for index, bullet in enumerate(narrative_bullets[:8], start=1):
                remedies.append(
                    {
                        "title": self._bullet_title(bullet),
                        "description": scrub_client_text(bullet.lstrip("• ").strip()),
                        "priority": min(index, 3),
                    }
                )
            return remedies

        for index, recommendation in enumerate(self.output.recommendations[:8], start=1):
            remedies.append(
                {
                    "title": self._humanize_token(recommendation.title),
                    "description": self._recommendation_description(recommendation),
                    "priority": recommendation.priority_rank,
                }
            )
        return remedies

    def overall_confidence(self) -> float:
        return self.output.overall_confidence

    def _format_priority(self, priority: ConsultationPriority) -> str:
        return localize(
            self.language,
            hi=(
                f"{priority.rank}. {priority.title}: {priority.rationale} "
                f"(विश्वास {int(round(priority.confidence * 100))}%)"
            ),
            en=(
                f"{priority.rank}. {priority.title}: {priority.rationale} "
                f"(confidence {int(round(priority.confidence * 100))}%)"
            ),
        )

    def _format_recommendation(self, recommendation: ConsultationRecommendation) -> str:
        description = self._recommendation_description(recommendation)
        return localize(
            self.language,
            hi=(
                f"{self._humanize_token(recommendation.title)} — {description} "
                f"(प्राथमिकता {recommendation.priority_rank}, "
                f"विश्वास {int(round(recommendation.confidence * 100))}%)"
            ),
            en=(
                f"{self._humanize_token(recommendation.title)} — {description} "
                f"(priority {recommendation.priority_rank}, "
                f"confidence {int(round(recommendation.confidence * 100))}%)"
            ),
        )

    def _recommendation_description(self, recommendation: ConsultationRecommendation) -> str:
        linked = self._evidence_text_for_ids(recommendation.evidence_ids)
        if linked:
            return linked
        narrative = self._clean_text(recommendation.narrative)
        if STRUCTURED_REASON_PATTERN.search(narrative):
            return localize(
                self.language,
                hi="उपलब्ध प्रमाणों के आधार पर यह सुझाव दिया गया है।",
                en="Suggested based on the available supporting evidence.",
            )
        return narrative or localize(
            self.language,
            hi="उपलब्ध प्रमाणों के आधार पर यह सुझाव दिया गया है।",
            en="Suggested based on the available supporting evidence.",
        )

    def _format_conflict(self, conflict: ConsultationConflict) -> str:
        return localize(
            self.language,
            hi=(
                f"संघर्ष: {conflict.description} — समाधान: {conflict.resolution} "
                f"(विश्वास {int(round(conflict.resolved_confidence * 100))}%)"
            ),
            en=(
                f"Conflict: {conflict.description} — resolution: {conflict.resolution} "
                f"(confidence {int(round(conflict.resolved_confidence * 100))}%)"
            ),
        )

    def _format_evidence(self, item: ConsultationEvidence) -> str:
        return localize(
            self.language,
            hi=f"{item.title}: {self._clean_text(item.summary)} (विश्वास {int(round(item.confidence * 100))}%)",
            en=f"{item.title}: {self._clean_text(item.summary)} (confidence {int(round(item.confidence * 100))}%)",
        )

    def _evidence_text_for_ids(self, evidence_ids: tuple[str, ...]) -> str:
        summaries: list[str] = []
        for evidence_id in evidence_ids:
            for item in self.output.evidence:
                if item.evidence_id == evidence_id and item.summary:
                    summaries.append(self._clean_text(item.summary))
                    break
        return " ".join(summaries[:2])

    @staticmethod
    def _clean_text(value: str | None) -> str:
        if not value:
            return ""
        cleaned = scrub_client_text(str(value))
        cleaned = STRUCTURED_REASON_PATTERN.sub("", cleaned).strip()
        return cleaned

    @staticmethod
    def _humanize_token(value: str) -> str:
        return value.replace("_", " ").strip().title()

    @staticmethod
    def _bullet_title(bullet: str) -> str:
        text = bullet.lstrip("• ").strip()
        if " (" in text:
            return text.split(" (", 1)[0].strip()
        if ":" in text:
            return text.split(":", 1)[0].strip()
        return text[:80]


def build_brain_context(
    consultation_brain_output: ConsultationBrainOutput | None,
    *,
    language: ReportLanguage,
) -> BrainReportContext | None:
    if consultation_brain_output is None:
        return None
    return BrainReportContext(output=consultation_brain_output, language=language)
