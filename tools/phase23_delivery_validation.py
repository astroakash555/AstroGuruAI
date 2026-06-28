"""Phase 23 validation: compare legacy vs master-consultation delivery on audited charts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.consultation_brain import ConsultationBrain, ConsultationInput
from backend.app.services.report_engine import ProfessionalReportBuilder, ProfessionalReportInput, ReportLanguage
from backend.app.services.report_engine.master_consultation_delivery import build_delivered_client_report
from backend.app.services.report_engine.serializers import professional_report_to_client_json
from reports.orchestrator import ReportOrchestrator
from reports.types import ReportInput
from tests.golden.loader import build_birth_data_for_case, load_golden_chart
from tools.phase22_quality_audit import (
    AUDIT_CHART_IDS,
    PROBLEM_TEXT,
    TECH_DUMP_PATTERNS,
    _collect_text_blobs,
    _find_duplicates,
    _report_input_for_case,
)

OUTPUT_PATH = ROOT / "tests/fixtures/golden_charts/phase23_delivery_validation_results.json"


def _legacy_client_report(unified: dict[str, Any], brain) -> dict[str, Any]:
    report_input = ProfessionalReportInput(
        unified_report=unified,
        remedy_generation={"remedies": []},
        problem_text=PROBLEM_TEXT,
        language=ReportLanguage.HINDI,
        consultation_brain_output=brain,
    )
    result = ProfessionalReportBuilder().build(report_input)
    return professional_report_to_client_json(result, report_input=report_input)


def _score_client_report(client_report: dict[str, Any]) -> dict[str, Any]:
    all_text = _collect_text_blobs(client_report, "")
    tech_hits = sum(1 for pattern in TECH_DUMP_PATTERNS if pattern.search(all_text))
    paragraphs = [str(section.get("narrative", "")) for section in client_report.get("sections") or []]
    duplicate_count = len(_find_duplicates(paragraphs))
    remedy_titles = [item.get("title") for item in client_report.get("remedies") or [] if item.get("title")]
    duplicate_remedies = len(remedy_titles) - len(set(remedy_titles))
    avg_narrative_len = (
        sum(len(str(section.get("narrative", ""))) for section in client_report.get("sections") or [])
        / max(len(client_report.get("sections") or []), 1)
    )
    return {
        "technical_dump_hits": tech_hits,
        "duplicate_paragraphs": duplicate_count,
        "duplicate_remedies": duplicate_remedies,
        "avg_section_narrative_chars": round(avg_narrative_len, 1),
        "delivery_mode": (client_report.get("metadata") or {}).get("delivery_mode"),
    }


def _excerpt(client_report: dict[str, Any]) -> dict[str, str]:
    sections = client_report.get("sections") or []
    by_id = {section.get("section_id"): section for section in sections}
    return {
        "birth": str((by_id.get("birth_details") or {}).get("narrative", ""))[:280],
        "problem": str((by_id.get("problem_analysis") or {}).get("narrative", ""))[:280],
        "remedies": str((by_id.get("personalized_remedies") or {}).get("narrative", ""))[:280],
        "summary": str((by_id.get("final_summary") or {}).get("narrative", ""))[:280],
    }


def main() -> int:
    orchestrator = ReportOrchestrator()
    results: list[dict[str, Any]] = []
    for chart_id in AUDIT_CHART_IDS:
        case = load_golden_chart(chart_id)
        unified = orchestrator.generate_json(_report_input_for_case(case))
        brain = ConsultationBrain().run(
            ConsultationInput(
                unified_report=unified,
                problem_text=PROBLEM_TEXT,
                professional_report=None,
                language="hi",
            )
        )
        legacy = _legacy_client_report(unified, brain)
        delivered = build_delivered_client_report(
            ProfessionalReportInput(
                unified_report=unified,
                remedy_generation={"remedies": []},
                problem_text=PROBLEM_TEXT,
                language=ReportLanguage.HINDI,
                consultation_brain_output=brain,
            )
        )
        legacy_score = _score_client_report(legacy)
        delivered_score = _score_client_report(delivered)
        results.append(
            {
                "chart_id": chart_id,
                "legacy": legacy_score,
                "delivered": delivered_score,
                "improvement": {
                    "technical_dump_hits_delta": legacy_score["technical_dump_hits"]
                    - delivered_score["technical_dump_hits"],
                    "duplicate_paragraphs_delta": legacy_score["duplicate_paragraphs"]
                    - delivered_score["duplicate_paragraphs"],
                    "duplicate_remedies_delta": legacy_score["duplicate_remedies"]
                    - delivered_score["duplicate_remedies"],
                },
                "excerpt_delivered": _excerpt(delivered),
            }
        )

    legacy_avg_tech = sum(item["legacy"]["technical_dump_hits"] for item in results) / len(results)
    delivered_avg_tech = sum(item["delivered"]["technical_dump_hits"] for item in results) / len(results)
    summary = {
        "charts_audited": len(results),
        "legacy_avg_technical_dump_hits": round(legacy_avg_tech, 2),
        "delivered_avg_technical_dump_hits": round(delivered_avg_tech, 2),
        "all_delivered_use_master_mode": all(
            item["delivered"]["delivery_mode"] == "master_consultation_v1" for item in results
        ),
        "charts": results,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "charts"}, indent=2))
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
