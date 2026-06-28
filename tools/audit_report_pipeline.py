"""Read-only audit trace for report rendering pipeline."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.report_engine.report_builder import ProfessionalReportBuilder
from backend.app.services.report_engine.serializers import section_to_client_dict, section_to_dict
from backend.app.services.report_engine.types import ProfessionalReportInput, ReportLanguage

SAMPLE = {
    "subject": {
        "birth_place": "Delhi",
        "timezone": "Asia/Kolkata",
        "latitude": 28.6,
        "longitude": 77.2,
        "datetime_utc": "1990-01-15T05:00:00Z",
    },
    "summary": {
        "lagna_sign": "Aries",
        "moon_sign": "Aries",
        "moon_nakshatra": "Ashwini",
        "current_mahadasha": "Saturn",
        "current_antardasha": "Venus",
        "reasoning_confidence_score": 82,
    },
    "kundali": {
        "ascendant": {
            "longitude": 5.0,
            "sign": {"name_en": "Aries", "degree_in_sign": 5.0},
            "nakshatra": {"name": "Ashwini", "pada": 1},
        },
        "planets": [
            {
                "name": "Moon",
                "longitude": 5.0,
                "sign": {"name_en": "Aries", "degree_in_sign": 5.0},
                "nakshatra": {"name": "Ashwini", "pada": 1},
                "house": 1,
                "is_retrograde": False,
            }
        ],
        "houses": [{"number": n, "sign": {"name_en": "Aries"}} for n in range(1, 13)],
    },
    "dasha": {
        "birth": {
            "birth_place": "Delhi",
            "timezone": "Asia/Kolkata",
            "date_of_birth": "1990-01-15",
            "birth_time": "10:30:00",
        },
        "moon": {"nakshatra": "Ashwini", "pada": 1, "lord": "Ketu"},
        "balance": {"lord": "Ketu"},
        "current": {
            "mahadasha": {
                "lord": "Saturn",
                "start": "2020-01-01T00:00:00Z",
                "end": "2039-01-01T00:00:00Z",
            },
            "antardasha": {
                "lord": "Venus",
                "start": "2024-01-01T00:00:00Z",
                "end": "2027-01-01T00:00:00Z",
            },
        },
    },
    "yogas": {"present_yogas": [], "summary": {"present_count": 0}},
    "transits": {"highlights": []},
    "problem_analysis": {"category": {"category": "marriage"}, "severity": {"level": "high"}},
    "fusion": {"confidence": 0.82, "root_causes": [{"title": "Saturn pressure"}]},
    "consultation_brain": {"executive_summary": "Patience needed", "strengths": [], "risks": []},
    "vedic": {"observations": []},
    "kp_analysis": {"events": [{"event_type": "marriage", "is_supported": True}]},
    "lal_kitab": {"dosh_findings": [{"finding_name": "Mars 8th House Dosh", "is_present": True}]},
}

inp = ProfessionalReportInput(
    unified_report=SAMPLE,
    remedy_generation={"remedies": [{"title": "Hanuman Chalisa", "priority": 1}]},
    problem_text="Marriage delay",
    language=ReportLanguage.HINDI,
)
builder = ProfessionalReportBuilder()
result = builder.build(inp)
payload = builder.build_json(inp)

print("STEP 1 ProfessionalReportBuilder.build()")
s0 = result.sections[0]
print("  Python type:", type(result).__name__)
print("  Section.facts type:", type(s0.facts).__name__)
print("  facts is dict/list/str/null:", type(s0.facts).__name__)
print("  Example facts:", json.dumps(s0.facts, ensure_ascii=False)[:180])

print("\nSTEP 1b section_to_dict (internal only)")
internal = section_to_dict(s0)
print("  facts type:", type(internal["facts"]).__name__)

print("\nSTEP 2 section_to_client_dict / serializers")
client_section = section_to_client_dict(s0, language=ReportLanguage.HINDI)
print("  facts type:", type(client_section["facts"]).__name__)
print("  Example:", json.dumps(client_section, ensure_ascii=False)[:280])

print("\nSTEP 3 build_json client payload")
for sec in payload["sections"]:
    ft = type(sec["facts"]).__name__
    print(f"  {sec['section_id']}: facts={ft}")

print("\nSTEP 4 JSON API round-trip")
api_json = json.loads(json.dumps(payload))
for sec in api_json["sections"]:
    print(f"  {sec['section_id']}: facts={type(sec['facts']).__name__}")

moon = next(s for s in api_json["sections"] if s["section_id"] == "moon_analysis")
print("\nExample moon_analysis payload:")
print(json.dumps(moon, ensure_ascii=False, indent=2))
