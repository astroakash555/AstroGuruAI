"""Generate Engine vs Reference comparison report for golden charts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from astrology_engine import VedicAstrologyEngine
from astrology_engine.dasha.serializer import to_json_dict
from tests.golden.helpers import build_birth_data, build_dasha_input_from_bundle
from tests.golden.comparator import compare_chart
from tests.golden.loader import GOLDEN_DIR, load_all_golden_charts, parse_reference_datetime

REPORT_PATH = Path(__file__).resolve().parents[1] / "docs" / "GOLDEN_CHART_COMPARISON_REPORT.md"


def _format_mismatch_table(mismatches: list) -> str:
    if not mismatches:
        return "_No mismatches._\n"
    lines = ["| Category | Field | Expected | Actual | Delta |", "|---|---|---|---|---|"]
    for item in mismatches:
        delta = f"{item.delta:.6f}" if item.delta is not None else "—"
        lines.append(
            f"| {item.category} | {item.field} | `{item.expected}` | `{item.actual}` | {delta} |"
        )
    return "\n".join(lines) + "\n"


def generate_report() -> str:
    engine = VedicAstrologyEngine()
    cases = load_all_golden_charts()
    results = []
    total_mismatches = 0
    astrosage_verified = 0
    astrosage_failed = 0

    for case in cases:
        birth_data = build_birth_data(
            date_of_birth=case.input.date_of_birth,
            birth_time=case.input.birth_time,
            latitude=case.input.latitude,
            longitude=case.input.longitude,
            timezone_name=case.input.timezone,
        )
        bundle = engine.compute_chart(birth_data)
        dasha_input = build_dasha_input_from_bundle(
            bundle,
            birth_place=case.input.place,
            timezone=case.input.timezone,
        )
        reference_dt = parse_reference_datetime(case.expected["dasha"].get("reference_datetime"))
        dasha_result = engine.compute_vimshottari_dasha(dasha_input, reference_datetime=reference_dt)
        dasha_payload = to_json_dict(dasha_result)
        comparison = compare_chart(case, bundle, dasha_payload)
        results.append((case, comparison))
        total_mismatches += len(comparison.mismatches)
        if case.input.source == "astrosage":
            if comparison.passed:
                astrosage_verified += 1
            else:
                astrosage_failed += 1

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    passed = sum(1 for _, result in results if result.passed)
    failed = len(results) - passed

    sections = [
        "# Golden Chart Comparison Report",
        "",
        f"_Generated: {generated_at}_",
        "",
        "## Summary",
        "",
        f"- Charts compared: **{len(results)}**",
        f"- Passed: **{passed}**",
        f"- Failed: **{failed}**",
        f"- Total field mismatches: **{total_mismatches}**",
        f"- AstroSage-verified charts passed: **{astrosage_verified}**",
        f"- AstroSage-verified charts failed: **{astrosage_failed}**",
        "",
        "Tolerances: planet/ascendant longitude `< 0.01°`; dasha start/end dates exact.",
        "",
        "## Chart Results",
        "",
    ]

    for case, comparison in results:
        status = "PASS" if comparison.passed else "FAIL"
        sections.extend(
            [
                f"### {case.input.name} (`{case.input.chart_id}`) — {status}",
                "",
                f"- Source: `{case.input.source}`",
                f"- Place: {case.input.place}",
                f"- Notes: {case.input.notes or '—'}",
                "",
            ]
        )
        if comparison.mismatches:
            sections.append("#### Mismatches")
            sections.append("")
            sections.append(_format_mismatch_table(comparison.mismatches))
        else:
            asc = case.expected["ascendant"]
            moon = case.expected["planets"]["Moon"]
            current = case.expected["dasha"]["current"]
            sections.extend(
                [
                    "#### Reference snapshot",
                    "",
                    f"- Ascendant: {asc['sign']} {asc['degree_in_sign']:.2f}° ({asc['longitude']:.6f}°)",
                    f"- Moon: {moon['sign']} / {moon['nakshatra']} pada {moon['pada']}",
                    f"- Current MD (2026 ref): {current['mahadasha']} / AD: {current['antardasha']}",
                    "",
                ]
            )

    sections.extend(
        [
            "## Mismatch Resolution",
            "",
            "| Chart | Status | Action |",
            "|---|---|---|",
        ]
    )
    for case, comparison in results:
        if comparison.passed:
            action = "Verified - no action required"
            if case.input.source == "engine_locked":
                action = "Engine-locked baseline - pending external AstroSage/JHora audit"
        else:
            action = "Requires investigation"
        sections.append(f"| {case.input.chart_id} | {'PASS' if comparison.passed else 'FAIL'} | {action} |")

    report = "\n".join(sections) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")

    summary_path = GOLDEN_DIR / "last_comparison_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "generated_at": generated_at,
                "charts": len(results),
                "passed": passed,
                "failed": failed,
                "total_mismatches": total_mismatches,
                "results": [
                    {
                        "chart_id": comparison.chart_id,
                        "passed": comparison.passed,
                        "mismatch_count": len(comparison.mismatches),
                        "source": comparison.source,
                    }
                    for _, comparison in results
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    report = generate_report()
    print(report)
    print(f"\nReport written to {REPORT_PATH}")
