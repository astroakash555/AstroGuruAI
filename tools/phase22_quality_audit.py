"""Phase 22 read-only end-to-end consultation quality audit (validation only)."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput, MasterConsultationEngine
from backend.app.services.report_engine import ProfessionalReportBuilder, ProfessionalReportInput, ReportLanguage
from backend.app.services.report_engine.serializers import professional_report_to_client_json
from reports.orchestrator import ReportOrchestrator
from reports.types import ReportInput
from tests.golden.loader import build_birth_data_for_case, load_golden_chart

AUDIT_CHART_IDS = [
    "poorvi_sharma_2016",
    "delhi_1990_1030",
    "mumbai_1985_0630",
    "chennai_1992_2145",
    "kolkata_1978_1200",
    "bangalore_2000_0000",
    "hyderabad_1988_1430",
    "pune_1995_0815",
    "ahmedabad_1970_1800",
    "jaipur_2005_1100",
]

PROBLEM_TEXT = "Career growth and stability"

RAW_JSON_PATTERNS = (
    re.compile(r"\{[^{}]*\"[a-z_]+\"\s*:"),
    re.compile(r"evidence_id\s*="),
    re.compile(r"category=[\w_]+\|"),
    re.compile(r"\[object Object\]"),
    re.compile(r"MappingProxyType"),
)

TECH_DUMP_PATTERNS = (
    re.compile(r"\bSun in \w+", re.I),
    re.compile(r"\bVenus Combust\b", re.I),
    re.compile(r"\bRaj Yoga\b", re.I),
    re.compile(r"\bHouse \d+\b", re.I),
    re.compile(r"supported\s*=\s*(true|false)", re.I),
    re.compile(r"is_supported", re.I),
)


def _report_input_for_case(case) -> ReportInput:
    return ReportInput(
        birth_data=build_birth_data_for_case(case),
        birth_place=case.input.place,
        problem_text=PROBLEM_TEXT,
        target_date=datetime(2026, 6, 15, tzinfo=timezone.utc).date(),
    )


def _dasha_dates(unified: dict[str, Any]) -> set[str]:
    dates: set[str] = set()
    dasha = unified.get("dasha") or {}
    current = dasha.get("current") or {}
    for key in ("mahadasha", "antardasha", "pratyantardasha"):
        block = current.get(key) or {}
        for field in ("start", "end"):
            value = block.get(field)
            if value:
                dates.add(str(value).split("T")[0])
    return dates


def _collect_text_blobs(client_report: dict[str, Any], master_text: str) -> str:
    parts: list[str] = [master_text]
    for key in (
        "problem_summary",
        "astrological_root_cause",
        "planet_analysis",
        "dasha_analysis",
        "transit_analysis",
        "kp_analysis",
        "lal_kitab_analysis",
        "short_term_outlook",
        "long_term_outlook",
    ):
        value = client_report.get(key)
        if isinstance(value, str):
            parts.append(value)
    for section in client_report.get("sections") or []:
        parts.append(str(section.get("title", "")))
        parts.append(str(section.get("narrative", "")))
        for fact in section.get("facts") or []:
            parts.append(str(fact))
    return "\n".join(parts)


def _find_duplicates(paragraphs: list[str], *, min_len: int = 40) -> list[str]:
    normalized = [re.sub(r"\s+", " ", p.strip().lower()) for p in paragraphs if len(p.strip()) >= min_len]
    counts = Counter(normalized)
    return [text for text, count in counts.items() if count > 1]


def _issues_for_chart(chart_id: str) -> dict[str, Any]:
    case = load_golden_chart(chart_id)
    orchestrator = ReportOrchestrator()
    unified = orchestrator.generate_json(_report_input_for_case(case))
    brain = ConsultationBrain().run(
        ConsultationInput(
            unified_report=unified,
            professional_report=None,
            problem_text=PROBLEM_TEXT,
            language="hi",
        )
    )
    builder = ProfessionalReportBuilder()
    report_input = ProfessionalReportInput(
        unified_report=unified,
        remedy_generation={"remedies": []},
        problem_text=PROBLEM_TEXT,
        language=ReportLanguage.HINDI,
        consultation_brain_output=brain,
    )
    report_result = builder.build(report_input)
    client_report = professional_report_to_client_json(report_result, report_input=report_input)
    master = MasterConsultationEngine().generate(
        brain,
        None,
        unified,
        language="hi",
        problem_text=PROBLEM_TEXT,
    )

    issues: list[dict[str, Any]] = []
    all_text = _collect_text_blobs(client_report, master.full_text)
    serialized = json.dumps(client_report, ensure_ascii=False, default=str) + master.full_text

    for pattern in RAW_JSON_PATTERNS:
        match = pattern.search(serialized)
        if match:
            issues.append(
                {
                    "severity": "HIGH",
                    "location": "client_report / master_consultation",
                    "example": match.group(0)[:120],
                    "suggested_fix": "Scrub or rephrase structured/internal payloads before client serialization.",
                    "rule": "no_raw_json",
                }
            )

    for pattern in TECH_DUMP_PATTERNS:
        match = pattern.search(all_text)
        if match:
            issues.append(
                {
                    "severity": "MEDIUM",
                    "location": "client_report narrative",
                    "example": match.group(0),
                    "suggested_fix": "Route planet/house/yoga facts through consultation brain phrasing layer.",
                    "rule": "no_technical_dump",
                }
            )

    paragraphs = [master.full_text]
    for section in client_report.get("sections") or []:
        paragraphs.append(str(section.get("narrative", "")))
    duplicates = _find_duplicates(paragraphs)
    for dup in duplicates[:3]:
        issues.append(
            {
                "severity": "MEDIUM",
                "location": "cross-section narrative",
                "example": dup[:120],
                "suggested_fix": "Deduplicate shared evidence sentences across dasha/transit/outlook sections.",
                "rule": "no_duplicated_paragraphs",
            }
        )

    remedy_titles = [item.get("title") for item in client_report.get("remedies") or [] if item.get("title")]
    if len(remedy_titles) != len(set(remedy_titles)):
        issues.append(
            {
                "severity": "LOW",
                "location": "client_report.remedies",
                "example": str(remedy_titles),
                "suggested_fix": "Collapse duplicate remedy categories in legacy remedies serializer.",
                "rule": "no_repeated_remedies",
            }
        )

    recs_without_evidence = [
        rec.recommendation_id
        for rec in brain.recommendations
        if not rec.evidence_ids and rec.confidence > 0
    ]
    if recs_without_evidence:
        issues.append(
            {
                "severity": "MEDIUM",
                "location": "ConsultationBrain recommendations",
                "example": recs_without_evidence[:3],
                "suggested_fix": "Attach evidence_ids to deferred/general recommendations or suppress them.",
                "rule": "recommendation_evidence",
            }
        )

    dasha_dates = _dasha_dates(unified)
    for date_token in re.findall(r"\d{4}-\d{2}-\d{2}", master.full_text):
        if date_token not in dasha_dates:
            issues.append(
                {
                    "severity": "HIGH",
                    "location": "MasterConsultation future outlook",
                    "example": date_token,
                    "suggested_fix": "Only surface dasha end dates present in unified_report.dasha.current.",
                    "rule": "no_hallucinated_timelines",
                }
            )
            break

    brain_conf = round(brain.overall_confidence, 2)
    report_conf = round(client_report.get("metadata", {}).get("overall_confidence", 0), 2)
    if abs(brain_conf - report_conf) > 0.05:
        issues.append(
            {
                "severity": "LOW",
                "location": "metadata.overall_confidence",
                "example": f"brain={brain_conf}, report={report_conf}",
                "suggested_fix": "Align report overall_confidence with ConsultationBrainOutput.overall_confidence.",
                "rule": "confidence_consistency",
            }
        )

    if PROBLEM_TEXT not in master.full_text and PROBLEM_TEXT not in client_report.get("problem_summary", ""):
        issues.append(
            {
                "severity": "MEDIUM",
                "location": "MasterConsultation greeting",
                "example": PROBLEM_TEXT,
                "suggested_fix": "Ensure client question appears in greeting and problem sections.",
                "rule": "client_question_answered",
            }
        )

    empty_sections = [
        section["section_id"]
        for section in client_report.get("sections") or []
        if not str(section.get("narrative", "")).strip()
    ]
    if empty_sections:
        issues.append(
            {
                "severity": "LOW",
                "location": "client_report.sections",
                "example": empty_sections,
                "suggested_fix": "Provide empathetic empty-state copy instead of blank narratives.",
                "rule": "missing_explanation",
            }
        )

    if len(client_report.get("sections") or []) != 14:
        issues.append(
            {
                "severity": "HIGH",
                "location": "client_report contract",
                "example": len(client_report.get("sections") or []),
                "suggested_fix": "Restore 14-section client_report contract.",
                "rule": "professional_flow",
            }
        )

    if len(master.sections) != 10:
        issues.append(
            {
                "severity": "HIGH",
                "location": "MasterConsultation",
                "example": len(master.sections),
                "suggested_fix": "Ensure 10-section master consultation flow.",
                "rule": "professional_flow",
            }
        )

    for section in client_report.get("sections") or []:
        facts = section.get("facts")
        if not isinstance(facts, list) or any(not isinstance(line, str) for line in facts):
            issues.append(
                {
                    "severity": "CRITICAL",
                    "location": f"section {section.get('section_id')}",
                    "example": type(facts).__name__,
                    "suggested_fix": "Facts must remain string arrays for API/PDF contract.",
                    "rule": "no_raw_json",
                }
            )
            break

    scores = _score_report(
        issues=issues,
        brain=brain,
        client_report=client_report,
        master=master,
        unified=unified,
    )
    return {
        "chart_id": chart_id,
        "name": case.input.name,
        "issue_count": len(issues),
        "issues": issues,
        "scores": scores,
        "evidence_count": len(brain.evidence),
        "priority_count": len(brain.priorities),
        "recommendation_count": len(brain.recommendations),
    }


def _score_report(*, issues, brain, client_report, master, unified) -> dict[str, int]:
    penalty = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3}
    total_penalty = sum(penalty.get(item["severity"], 5) for item in issues)

    astro = max(0, 100 - total_penalty // 2)
    explanation = max(0, 100 - total_penalty)
    if brain.priorities and brain.evidence:
        explanation = min(100, explanation + 5)
    natural = max(0, 100 - sum(p["severity"] == "MEDIUM" and p["rule"] == "no_technical_dump" for p in issues) * 10)
    tone = max(0, 100 - len([i for i in issues if i["rule"] == "no_duplicated_paragraphs"]) * 8)
    traceability = max(0, 100 - len([i for i in issues if i["rule"] in {"recommendation_evidence", "no_hallucinated_timelines"}]) * 12)
    usefulness = max(0, 100 - total_penalty // 3)
    if PROBLEM_TEXT in master.full_text:
        usefulness = min(100, usefulness + 5)
    if not brain.priorities:
        usefulness = max(0, usefulness - 10)

    return {
        "astrological_correctness": astro,
        "explanation_quality": explanation,
        "natural_language": natural,
        "professional_tone": tone,
        "evidence_traceability": traceability,
        "client_usefulness": usefulness,
        "overall": round(
            (
                astro
                + explanation
                + natural
                + tone
                + traceability
                + usefulness
            )
            / 6
        ),
    }


def main() -> None:
    pytest = __import__("pytest")
    pytest.importorskip("swisseph")
    results = [_issues_for_chart(chart_id) for chart_id in AUDIT_CHART_IDS]
    output_path = ROOT / "tests" / "fixtures" / "golden_charts" / "phase22_quality_audit_results.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"charts_audited": len(results), "output": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
