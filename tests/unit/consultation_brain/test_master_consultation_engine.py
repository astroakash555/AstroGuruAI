"""Tests for the master astrologer conversation engine."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.master_consultation_engine import (
    MasterConsultationEngine,
    _humanize,
    _resolve_problem_text,
)
from backend.app.services.consultation_brain.master_consultation_i18n import normalize_language, section_title
from backend.app.services.consultation_brain.master_consultation_models import (
    MasterConsultationLanguage,
    MasterConsultationSectionId,
)
from backend.app.services.consultation_brain.models import (
    ConsultationBrainOutput,
    ConsultationConflict,
    ConsultationEvidence,
    ConsultationPriority,
    ConsultationRecommendation,
)
from backend.app.services.consultation_brain.constants import PipelineStage

FORBIDDEN_PATTERNS = (
    r"category=[\w_]+\|domain=",
    r"\bSun in Taurus\b",
    r"\bRaj Yoga\b",
    r"\bHouse 8\b",
)


def _brain_output(sample_unified_report, sample_consultation_input):
    return ConsultationBrain().run(sample_consultation_input)


def test_master_consultation_generates_ten_sections(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    assert len(consultation.sections) == 10
    assert [section.section_id for section in consultation.sections] == list(MasterConsultationSectionId)
    assert consultation.language is MasterConsultationLanguage.HINDI
    assert consultation.full_text
    assert consultation.section_titles[0] == section_title(MasterConsultationSectionId.GREETING, MasterConsultationLanguage.HINDI)


def test_master_consultation_mentions_client_question(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    greeting = consultation.sections[0].paragraphs[0]
    understanding = consultation.sections[1].paragraphs[0]
    assert "Marriage delay" in greeting
    assert "Marriage delay" in understanding


def test_master_consultation_supports_english_and_hinglish(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    engine = MasterConsultationEngine()
    english = engine.generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="en",
        problem_text="Marriage delay",
    )
    hinglish = engine.generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hinglish",
        problem_text="Marriage delay",
    )
    assert english.language is MasterConsultationLanguage.ENGLISH
    assert hinglish.language is MasterConsultationLanguage.HINGLISH
    assert english.sections[0].paragraphs[0].startswith("Welcome")
    assert hinglish.sections[0].paragraphs[0].startswith("Namaste")


def test_master_consultation_uses_evidence_without_technical_dumps(
    sample_unified_report,
    sample_consultation_input,
):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="en",
        problem_text="Marriage delay",
    )
    serialized = json.dumps(consultation.full_text, ensure_ascii=False)
    for pattern in FORBIDDEN_PATTERNS:
        assert re.search(pattern, serialized, re.IGNORECASE) is None, pattern


def test_master_consultation_includes_remedies_and_priorities(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    remedies = consultation.sections[7]
    assert remedies.section_id is MasterConsultationSectionId.REMEDIES
    assert remedies.paragraphs
    why = consultation.sections[2]
    assert why.paragraphs


def test_master_consultation_is_deterministic(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    engine = MasterConsultationEngine()
    first = engine.generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    second = engine.generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    assert first == second


def test_master_consultation_handles_empty_brain_output():
    empty = ConsultationBrainOutput(
        generated_at=datetime(2026, 6, 15, 12, 0, tzinfo=UTC),
        stage_trace=(PipelineStage.PRODUCE_OUTPUT,),
        evidence=(),
        conflicts=(),
        priorities=(),
        recommendations=(),
        overall_confidence=0.0,
        executive_summary="No evidence.",
        narrative=None,
    )
    consultation = MasterConsultationEngine().generate(empty, None, {}, language="en")
    assert len(consultation.sections) == 10
    assert consultation.sections[2].paragraphs[0].startswith("No specific cause")


def test_master_consultation_includes_conflicts_when_present():
    evidence = ConsultationEvidence(
        evidence_id="ev-1",
        source=EvidenceSource.KP,
        category=EvidenceCategory.RELATIONSHIP,
        title="Mixed signal",
        summary="Marriage timing appears delayed in current signals.",
        weight=0.4,
        confidence=0.5,
    )
    brain_output = ConsultationBrainOutput(
        generated_at=datetime(2026, 6, 15, 12, 0, tzinfo=UTC),
        stage_trace=(PipelineStage.PRODUCE_OUTPUT,),
        evidence=(evidence,),
        conflicts=(
            ConsultationConflict(
                conflict_id="c1",
                evidence_ids=("ev-1",),
                description="Positive and negative marriage signals conflict.",
                resolution="Weighted resolution favors caution.",
                resolved_confidence=0.6,
            ),
        ),
        priorities=(
            ConsultationPriority(
                rank=1,
                domain="marriage",
                title="Marriage",
                rationale="Primary focus area.",
                confidence=0.7,
                evidence_ids=("ev-1",),
            ),
        ),
        recommendations=(
            ConsultationRecommendation(
                recommendation_id="r1",
                title="marriage_advice",
                narrative="category=marriage_advice|domain=marriage|domain_rank=1|evidence_count=1|source_count=1|conflict_resolved=false|score=0.5000",
                priority_rank=1,
                confidence=0.6,
                evidence_ids=("ev-1",),
                action_items=("marriage_advice", "high"),
            ),
        ),
        overall_confidence=0.6,
        executive_summary="Summary",
        narrative=None,
    )
    consultation = MasterConsultationEngine().generate(
        brain_output,
        None,
        {
            "dasha": {
                "current": {
                    "mahadasha": {"end": "2030-01-01T00:00:00Z"},
                    "antardasha": {"end": "2027-01-01T00:00:00Z"},
                }
            }
        },
        language="en",
        problem_text="Marriage delay",
    )
    serialized = consultation.full_text
    assert "conflict" in serialized.lower() or "mixed" in serialized.lower()
    assert consultation.sections[7].paragraphs
    assert "category=" not in serialized


def test_normalize_language_aliases():
    assert normalize_language(None) is MasterConsultationLanguage.HINDI
    assert normalize_language("english") is MasterConsultationLanguage.ENGLISH
    assert normalize_language("hi-en") is MasterConsultationLanguage.HINGLISH


def test_humanize_strips_structured_reasons():
    assert "category=" not in _humanize(
        "category=marriage_advice|domain=marriage|domain_rank=1|evidence_count=1|source_count=1|conflict_resolved=false|score=0.5000"
    )


def test_resolve_problem_text_from_unified_report():
    assert _resolve_problem_text(None, {"problem_analysis": {"problem_text": "Career growth"}}, None) == "Career growth"


def test_master_consultation_section_body_text(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    section = consultation.sections[9]
    assert section.body_text
    assert "आशीर्वाद" in section.title or section.paragraphs


def test_master_consultation_future_outlook_includes_multiple_horizons(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="en",
        problem_text="Marriage delay",
    )
    outlook = consultation.sections[6]
    text = outlook.body_text
    assert "Short term" in text or "Medium term" in text or "Long term" in text


def test_master_consultation_uses_narrative_for_practical_and_closing(sample_unified_report, sample_consultation_input):
    brain_output = _brain_output(sample_unified_report, sample_consultation_input)
    consultation = MasterConsultationEngine().generate(
        brain_output,
        sample_consultation_input.professional_report,
        sample_unified_report,
        language="hi",
        problem_text="Marriage delay",
    )
    assert brain_output.narrative is not None
    assert consultation.sections[8].paragraphs
    assert consultation.sections[9].paragraphs


def test_master_consultation_resolves_problem_from_professional_report():
    brain_output = ConsultationBrainOutput(
        generated_at=datetime(2026, 6, 15, 12, 0, tzinfo=UTC),
        stage_trace=(PipelineStage.PRODUCE_OUTPUT,),
        evidence=(),
        conflicts=(),
        priorities=(),
        recommendations=(),
        overall_confidence=0.0,
        executive_summary="Summary",
        narrative=None,
    )
    consultation = MasterConsultationEngine().generate(
        brain_output,
        {
            "sections": [
                {"section_id": "summary", "facts": ["General summary"], "narrative": "Fallback narrative"},
                {"section_id": "problem_analysis", "facts": ["Career stagnation"]},
            ]
        },
        {},
        language="en",
    )
    assert "Career stagnation" in consultation.full_text or "General summary" in consultation.full_text


def test_i18n_templates_without_problem_text():
    from backend.app.services.consultation_brain.master_consultation_i18n import empathy_paragraph, greeting_paragraph

    assert "स्वागत" in greeting_paragraph(language=MasterConsultationLanguage.HINDI, problem_text=None)
    assert "swagat" in greeting_paragraph(language=MasterConsultationLanguage.HINGLISH, problem_text=None).lower()
    assert empathy_paragraph(language=MasterConsultationLanguage.HINDI, problem_text=None)
    assert empathy_paragraph(language=MasterConsultationLanguage.HINGLISH, problem_text=None)
    assert normalize_language("fr") is MasterConsultationLanguage.HINDI


def test_helper_edge_cases():
    from backend.app.services.consultation_brain.master_consultation_engine import _format_date, _join_flowing_paragraph

    assert _humanize("") == ""
    assert _humanize(None) == ""
    assert _join_flowing_paragraph([], language=MasterConsultationLanguage.ENGLISH) == ""
    assert _format_date("2030-01-01") == "2030-01-01"
    assert _resolve_problem_text(None, {}, {"sections": [{"section_id": "other"}]}) is None
