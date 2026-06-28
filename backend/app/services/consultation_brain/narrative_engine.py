"""Human consultation narrative engine for consultation brain."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.models import ConsultationEvidence, ConsultationEvidenceBundle
from backend.app.services.consultation_brain.narrative_i18n import (
    category_label,
    closing_paragraph,
    conflict_resolution_bullet,
    domain_label,
    empty_section_paragraph,
    evidence_bullet,
    evidence_intro,
    greeting_paragraph,
    normalize_language,
    priority_intro,
    recommendation_bullet,
    section_title,
)
from backend.app.services.consultation_brain.narrative_models import (
    ConsultationNarrative,
    NarrativeLanguage,
    NarrativeSection,
    NarrativeSectionId,
    NARRATIVE_SECTION_ORDER,
)
from backend.app.services.consultation_brain.priority_models import ConsultationPriorityResult
from backend.app.services.consultation_brain.recommendation_models import (
    ConsultationRecommendationResult,
    StructuredRecommendation,
)


class NarrativeEngine:
    """Generates warm, evidence-bound consultation narratives in supported languages."""

    def generate(
        self,
        recommendation_result: ConsultationRecommendationResult,
        priority_result: ConsultationPriorityResult,
        conflict_result: ConflictEngineResult,
        evidence_bundle: ConsultationEvidenceBundle,
        professional_report: Mapping[str, Any] | None,
        *,
        language: str = "hi",
        problem_text: str | None = None,
    ) -> ConsultationNarrative:
        resolved_language = normalize_language(language)
        evidence_by_id = _index_evidence(evidence_bundle.all_evidence)
        report_sections = _professional_report_sections(professional_report)
        builders = {
            NarrativeSectionId.GREETING: lambda: _build_greeting(resolved_language, problem_text),
            NarrativeSectionId.OVERALL_CHART_IMPRESSION: lambda: _build_overall_impression(
                resolved_language,
                evidence_bundle,
                report_sections,
            ),
            NarrativeSectionId.HIGHEST_PRIORITY_TOPIC: lambda: _build_highest_priority(
                resolved_language,
                priority_result,
            ),
            NarrativeSectionId.SUPPORTING_EVIDENCE: lambda: _build_supporting_evidence(
                resolved_language,
                priority_result,
                evidence_by_id,
                conflict_result,
            ),
            NarrativeSectionId.DASHA_DISCUSSION: lambda: _build_source_section(
                resolved_language,
                evidence_bundle.dasha,
                NarrativeSectionId.DASHA_DISCUSSION,
            ),
            NarrativeSectionId.TRANSIT_DISCUSSION: lambda: _build_source_section(
                resolved_language,
                evidence_bundle.transit,
                NarrativeSectionId.TRANSIT_DISCUSSION,
            ),
            NarrativeSectionId.YOGAS: lambda: _build_source_section(
                resolved_language,
                evidence_bundle.yogas,
                NarrativeSectionId.YOGAS,
            ),
            NarrativeSectionId.PRACTICAL_GUIDANCE: lambda: _build_practical_guidance(
                resolved_language,
                recommendation_result,
            ),
            NarrativeSectionId.RECOMMENDATIONS: lambda: _build_recommendations(
                resolved_language,
                recommendation_result,
            ),
            NarrativeSectionId.CLOSING_SUMMARY: lambda: _build_closing(
                resolved_language,
                priority_result,
                recommendation_result,
                evidence_bundle,
            ),
        }
        sections = tuple(
            _finalize_section(section_id, builders[section_id](), resolved_language)
            for section_id in NARRATIVE_SECTION_ORDER
        )
        return ConsultationNarrative(
            language=resolved_language,
            sections=sections,
            metadata={
                "section_count": len(sections),
                "evidence_count": evidence_bundle.evidence_count,
                "priority_count": len(priority_result.priorities),
                "recommendation_count": len(recommendation_result.all_recommendations),
                "conflict_resolution_count": len(conflict_result.resolutions),
                "professional_report_section_count": len(report_sections),
            },
        )


def _finalize_section(
    section_id: NarrativeSectionId,
    draft: tuple[tuple[str, ...], tuple[str, ...]],
    language: NarrativeLanguage,
) -> NarrativeSection:
    paragraphs, bullets = draft
    return NarrativeSection(
        section_id=section_id,
        title=section_title(section_id, language),
        paragraphs=paragraphs,
        bullets=bullets,
    )


def _build_greeting(language: NarrativeLanguage, problem_text: str | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (greeting_paragraph(language=language, problem_text=problem_text),), ()


def _build_overall_impression(
    language: NarrativeLanguage,
    evidence_bundle: ConsultationEvidenceBundle,
    report_sections: tuple[dict[str, Any], ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    bullets: list[str] = []
    for section in report_sections:
        title = _safe_text(section.get("title") or section.get("heading") or section.get("section_id"))
        facts = section.get("facts") or section.get("key_points") or []
        fact_lines = [_safe_text(fact) for fact in facts if _safe_text(fact)]
        summary = " ".join(fact_lines[:3]) or _safe_text(section.get("summary"))
        if title and summary:
            bullets.append(evidence_bullet(title=title, summary=summary, language=language))
    for item in evidence_bundle.professional_report:
        bullets.append(evidence_bullet(title=item.title, summary=item.summary, language=language))
    for item in evidence_bundle.fusion[:2]:
        bullets.append(evidence_bullet(title=item.title, summary=item.summary, language=language))
    if not bullets:
        return (empty_section_paragraph(section_id=NarrativeSectionId.OVERALL_CHART_IMPRESSION, language=language),), ()
    return (evidence_intro(language),), tuple(bullets)


def _build_highest_priority(
    language: NarrativeLanguage,
    priority_result: ConsultationPriorityResult,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    highest = priority_result.highest_priority
    if highest is None:
        return (
            empty_section_paragraph(section_id=NarrativeSectionId.HIGHEST_PRIORITY_TOPIC, language=language),
        ), ()
    label = domain_label(highest.domain, language)
    paragraph = priority_intro(domain_label_text=label, score=highest.priority_score, language=language)
    bullets = (
        evidence_bullet(
            title=label,
            summary=(
                f"urgency={highest.urgency:.2f}; importance={highest.importance:.2f}; "
                f"confidence={highest.confidence:.2f}; evidence_count={highest.evidence_count}"
            ),
            language=language,
        ),
    )
    return (paragraph,), bullets


def _build_supporting_evidence(
    language: NarrativeLanguage,
    priority_result: ConsultationPriorityResult,
    evidence_by_id: Mapping[str, ConsultationEvidence],
    conflict_result: ConflictEngineResult,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    highest = priority_result.highest_priority
    if highest is None:
        return (
            empty_section_paragraph(section_id=NarrativeSectionId.SUPPORTING_EVIDENCE, language=language),
        ), ()
    bullets: list[str] = []
    for evidence_id in highest.evidence_ids:
        item = evidence_by_id.get(evidence_id)
        if item is None:
            continue
        bullets.append(evidence_bullet(title=item.title, summary=item.summary, language=language))
    for resolution in conflict_result.resolutions:
        if resolution.resolved_signal.evidence_id in highest.evidence_ids:
            bullets.append(
                conflict_resolution_bullet(
                    conflict_type=resolution.conflict_type,
                    reason=resolution.resolution_reason,
                    language=language,
                )
            )
    if not bullets:
        return (
            empty_section_paragraph(section_id=NarrativeSectionId.SUPPORTING_EVIDENCE, language=language),
        ), ()
    return (evidence_intro(language),), tuple(bullets)


def _build_source_section(
    language: NarrativeLanguage,
    evidence_items: Sequence[ConsultationEvidence],
    section_id: NarrativeSectionId,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not evidence_items:
        return (empty_section_paragraph(section_id=section_id, language=language),), ()
    bullets = tuple(
        evidence_bullet(title=item.title, summary=item.summary, language=language)
        for item in sorted(evidence_items, key=lambda item: item.evidence_id)
    )
    return (evidence_intro(language),), bullets


def _build_practical_guidance(
    language: NarrativeLanguage,
    recommendation_result: ConsultationRecommendationResult,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    actionable = _actionable_recommendations(recommendation_result)
    if not actionable:
        return (empty_section_paragraph(section_id=NarrativeSectionId.PRACTICAL_GUIDANCE, language=language),), ()
    bullets = tuple(_format_recommendation(item, language) for item in actionable)
    return (evidence_intro(language),), bullets


def _build_recommendations(
    language: NarrativeLanguage,
    recommendation_result: ConsultationRecommendationResult,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    items = recommendation_result.all_recommendations
    if not items:
        return (empty_section_paragraph(section_id=NarrativeSectionId.RECOMMENDATIONS, language=language),), ()
    bullets = tuple(_format_recommendation(item, language) for item in items)
    return (evidence_intro(language),), bullets


def _build_closing(
    language: NarrativeLanguage,
    priority_result: ConsultationPriorityResult,
    recommendation_result: ConsultationRecommendationResult,
    evidence_bundle: ConsultationEvidenceBundle,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    paragraph = closing_paragraph(
        language=language,
        priority_count=len(priority_result.priorities),
        recommendation_count=len(recommendation_result.all_recommendations),
        evidence_count=evidence_bundle.evidence_count,
    )
    return (paragraph,), ()


def _format_recommendation(item: StructuredRecommendation, language: NarrativeLanguage) -> str:
    label = category_label(item.category, language)
    return recommendation_bullet(
        label=label,
        confidence=item.confidence,
        evidence_count=len(item.supporting_evidence_ids),
        language=language,
    )


def _actionable_recommendations(
    recommendation_result: ConsultationRecommendationResult,
) -> tuple[StructuredRecommendation, ...]:
    return recommendation_result.high_priority + recommendation_result.medium_priority


def _index_evidence(evidence: Sequence[ConsultationEvidence]) -> dict[str, ConsultationEvidence]:
    return {item.evidence_id: item for item in evidence}


def _professional_report_sections(
    professional_report: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(professional_report, dict):
        return ()
    sections = professional_report.get("sections") or []
    return tuple(section for section in sections if isinstance(section, dict))


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
