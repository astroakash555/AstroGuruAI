"""Tests for the human consultation narrative engine."""

from backend.app.services.consultation_brain.conflict_engine import ConflictEngineResult
from backend.app.services.consultation_brain.constants import EvidenceCategory, EvidenceSource
from backend.app.services.consultation_brain.models import ConsultationConflictResolution, ConsultationEvidence, ConsultationEvidenceBundle
from backend.app.services.consultation_brain.narrative_engine import NarrativeEngine
from backend.app.services.consultation_brain.narrative_i18n import normalize_language, section_title
from backend.app.services.consultation_brain.narrative_models import NarrativeLanguage, NarrativeSectionId
from backend.app.services.consultation_brain.priority_models import ConsultationPriorityResult, DomainPriority, PriorityDomain
from backend.app.services.consultation_brain.recommendation_engine import RecommendationEngine


def _evidence(**kwargs) -> ConsultationEvidence:
    defaults = {
        "evidence_id": "marriage-1",
        "source": EvidenceSource.RULE_STUDIO,
        "category": EvidenceCategory.RELATIONSHIP,
        "title": "Marriage delay indicator",
        "summary": "Rule studio indicates delayed marriage timing.",
        "weight": 0.5,
        "confidence": 0.8,
        "metadata": {"domain": "marriage"},
    }
    defaults.update(kwargs)
    return ConsultationEvidence(**defaults)


def _priority_result() -> ConsultationPriorityResult:
    marriage = DomainPriority(
        domain=PriorityDomain.MARRIAGE,
        rank=1,
        priority_score=0.82,
        urgency=0.75,
        importance=0.78,
        evidence_count=1,
        confidence=0.8,
        supporting_sources=(EvidenceSource.RULE_STUDIO,),
        evidence_ids=("marriage-1",),
    )
    return ConsultationPriorityResult(
        priorities=(marriage,),
        highest_priority=marriage,
        secondary_priorities=(),
        suppressed_topics=(PriorityDomain.LEGAL,),
    )


def _full_inputs():
    evidence = _evidence()
    dasha = _evidence(
        evidence_id="dasha-1",
        source=EvidenceSource.DASHA,
        category=EvidenceCategory.TIMING,
        title="Saturn Mahadasha",
        summary="Current Saturn period active.",
    )
    transit = _evidence(
        evidence_id="transit-1",
        source=EvidenceSource.TRANSIT,
        category=EvidenceCategory.TIMING,
        title="Saturn transit",
        summary="Saturn influencing 7th house.",
    )
    yoga = _evidence(
        evidence_id="yoga-1",
        source=EvidenceSource.YOGAS,
        category=EvidenceCategory.GENERAL,
        title="Gaj Kesari Yoga",
        summary="Moon and Jupiter yoga present.",
    )
    fusion = _evidence(
        evidence_id="fusion-1",
        source=EvidenceSource.FUSION,
        category=EvidenceCategory.RELATIONSHIP,
        title="Mixed marriage signals",
        summary="Fusion notes mixed indicators.",
    )
    bundle = ConsultationEvidenceBundle(
        rule_studio=(evidence,),
        dasha=(dasha,),
        transit=(transit,),
        yogas=(yoga,),
        fusion=(fusion,),
    )
    priority = _priority_result()
    conflict = ConflictEngineResult(resolutions=(), resolved_evidence=(evidence,), legacy_conflicts=())
    recommendation = RecommendationEngine().generate(priority, conflict, bundle)
    report = {
        "sections": [
            {
                "section_id": "summary",
                "title": "Executive Summary",
                "facts": ["Marriage delay indicated.", "Saturn influence on 7th house."],
            }
        ]
    }
    return recommendation, priority, conflict, bundle, report


def test_narrative_engine_greeting_without_problem_text():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    narrative = NarrativeEngine().generate(
        recommendation, priority, conflict, bundle, report, language="hi", problem_text=None
    )
    assert "नमस्ते" in narrative.sections[0].paragraphs[0]
    assert "Marriage delay" not in narrative.sections[0].paragraphs[0]


def test_narrative_engine_generates_ten_sections_in_order():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    narrative = NarrativeEngine().generate(
        recommendation,
        priority,
        conflict,
        bundle,
        report,
        language="hi",
        problem_text="Marriage delay",
    )
    assert len(narrative.sections) == 10
    assert [section.section_id for section in narrative.sections] == [
        NarrativeSectionId.GREETING,
        NarrativeSectionId.OVERALL_CHART_IMPRESSION,
        NarrativeSectionId.HIGHEST_PRIORITY_TOPIC,
        NarrativeSectionId.SUPPORTING_EVIDENCE,
        NarrativeSectionId.DASHA_DISCUSSION,
        NarrativeSectionId.TRANSIT_DISCUSSION,
        NarrativeSectionId.YOGAS,
        NarrativeSectionId.PRACTICAL_GUIDANCE,
        NarrativeSectionId.RECOMMENDATIONS,
        NarrativeSectionId.CLOSING_SUMMARY,
    ]
    assert narrative.language is NarrativeLanguage.HINDI
    assert narrative.section_titles[0] == section_title(NarrativeSectionId.GREETING, NarrativeLanguage.HINDI)
    assert "Marriage delay" in narrative.sections[0].paragraphs[0]
    assert narrative.full_text


def test_narrative_engine_uses_only_existing_evidence_text():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    narrative = NarrativeEngine().generate(
        recommendation,
        priority,
        conflict,
        bundle,
        report,
        language="en",
        problem_text="Marriage delay",
    )
    supporting = narrative.sections[3]
    assert any("Marriage delay indicator" in bullet for bullet in supporting.bullets)
    dasha = narrative.sections[4]
    assert any("Saturn Mahadasha" in bullet for bullet in dasha.bullets)
    yogas = narrative.sections[6]
    assert any("Gaj Kesari Yoga" in bullet for bullet in yogas.bullets)


def test_narrative_engine_supports_hinglish_and_english():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    hinglish = NarrativeEngine().generate(
        recommendation, priority, conflict, bundle, report, language="hinglish"
    )
    english = NarrativeEngine().generate(
        recommendation, priority, conflict, bundle, report, language="en"
    )
    assert hinglish.language is NarrativeLanguage.HINGLISH
    assert english.language is NarrativeLanguage.ENGLISH
    assert hinglish.sections[0].paragraphs[0].startswith("Namaste")
    assert english.sections[0].paragraphs[0].startswith("Welcome")


def test_normalize_language_defaults_and_aliases():
    assert normalize_language(None) is NarrativeLanguage.HINDI
    assert normalize_language("hin") is NarrativeLanguage.HINDI
    assert normalize_language("hi-en") is NarrativeLanguage.HINGLISH
    assert normalize_language("english") is NarrativeLanguage.ENGLISH
    assert normalize_language("fr") is NarrativeLanguage.HINDI


def test_narrative_engine_empty_inputs_use_empty_section_messages():
    narrative = NarrativeEngine().generate(
        RecommendationEngine().generate(
            ConsultationPriorityResult(
                priorities=(),
                highest_priority=None,
                secondary_priorities=(),
                suppressed_topics=(),
            ),
            ConflictEngineResult(resolutions=(), resolved_evidence=(), legacy_conflicts=()),
            ConsultationEvidenceBundle(),
        ),
        ConsultationPriorityResult(
            priorities=(),
            highest_priority=None,
            secondary_priorities=(),
            suppressed_topics=(),
        ),
        ConflictEngineResult(resolutions=(), resolved_evidence=(), legacy_conflicts=()),
        ConsultationEvidenceBundle(),
        None,
        language="en",
    )
    assert "No primary topic" in narrative.sections[2].paragraphs[0]
    assert "No dasha-related evidence" in narrative.sections[4].paragraphs[0]


def test_narrative_engine_includes_conflict_resolution_in_supporting_evidence():
    evidence = _evidence()
    resolution = ConsultationConflictResolution(
        resolution_id="conflict-1",
        conflict_type="positive_vs_negative",
        resolved_signal=evidence,
        winning_sources=(EvidenceSource.RULE_STUDIO,),
        losing_sources=(EvidenceSource.KP,),
        resolution_reason="weighted resolution",
        confidence=0.8,
        evidence_ids=("marriage-1", "kp-1"),
    )
    priority = _priority_result()
    bundle = ConsultationEvidenceBundle(rule_studio=(evidence,))
    recommendation = RecommendationEngine().generate(
        priority,
        ConflictEngineResult(
            resolutions=(resolution,),
            resolved_evidence=(evidence,),
            legacy_conflicts=(),
        ),
        bundle,
    )
    narrative = NarrativeEngine().generate(
        recommendation,
        priority,
        ConflictEngineResult(
            resolutions=(resolution,),
            resolved_evidence=(evidence,),
            legacy_conflicts=(),
        ),
        bundle,
        None,
        language="en",
    )
    supporting = narrative.sections[3]
    assert any("weighted resolution" in bullet for bullet in supporting.bullets)


def test_narrative_engine_is_deterministic():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    engine = NarrativeEngine()
    first = engine.generate(recommendation, priority, conflict, bundle, report, language="hi")
    second = engine.generate(recommendation, priority, conflict, bundle, report, language="hi")
    assert first == second


def test_narrative_section_body_text_combines_paragraphs_and_bullets():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    narrative = NarrativeEngine().generate(
        recommendation, priority, conflict, bundle, report, language="en"
    )
    section = narrative.sections[4]
    assert section.body_text
    assert "•" in section.body_text or section.paragraphs


def test_narrative_engine_metadata_counts():
    recommendation, priority, conflict, bundle, report = _full_inputs()
    narrative = NarrativeEngine().generate(
        recommendation, priority, conflict, bundle, report, language="hi"
    )
    assert narrative.metadata["section_count"] == 10
    assert narrative.metadata["evidence_count"] == bundle.evidence_count
    assert narrative.metadata["professional_report_section_count"] == 1
