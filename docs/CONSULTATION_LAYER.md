# Consultation Layer

Multi-agent senior astrologer consultation system for AstroGuruAI. Produces structured JSON only — no marketing text and no unsupported claims.

## Architecture

```
consultation_layer/
├── engine.py                    # ConsultationEngine orchestrator
├── types.py                     # ConsultationInput, AgentFinding, ConsultationResult
├── constants.py                 # Agent IDs and thresholds
├── agents/
│   ├── vedic.py                 # Agent 1 — Vedic Astrologer
│   ├── kp.py                    # Agent 2 — KP Astrologer
│   ├── lal_kitab.py             # Agent 3 — Lal Kitab Expert
│   ├── problem_specialist.py    # Agent 4 — Problem Specialist
│   ├── senior_guru.py           # Agent 5 — Senior Astro Guru
│   └── self_review.py           # Self Review Agent
└── serializers/
    ├── schemas.py               # Pydantic ConsultationJSON contract
    └── serializer.py            # to_json_dict / to_json_string
```

## Agent Responsibilities

| Agent | ID | Output Sections |
|-------|-----|-----------------|
| Vedic Astrologer | `vedic_astrologer` | `kundali_analysis`, `dasha_analysis`, `yoga_findings`, `dosha_findings` |
| KP Astrologer | `kp_astrologer` | `cuspal_analysis`, `significator_analysis`, `event_timing` |
| Lal Kitab Expert | `lal_kitab_expert` | `rin_analysis`, `dosh_analysis`, `remedy_selection` |
| Problem Specialist | `problem_specialist` | `problem_understanding`, `hidden_problem`, `matched_rule_groups` |
| Senior Astro Guru | `senior_astro_guru` | `compared_findings`, `resolved_conflicts`, `strongest_causes`, `strongest_remedies`, `final_conclusion` |
| Self Review Agent | `self_review_agent` | `contradictions_found`, `missing_evidence`, `weak_remedies`, `unsupported_conclusions`, `review_score` |

## Pipeline

```
Unified Report JSON
  → Agent 1–4 (specialist findings)
  → Agent 5 (Senior Guru synthesis + conflict resolution)
  → Self Review Agent (quality audit)
  → ConsultationJSON
```

Knowledge Brain rule matching is auto-enriched when `problem_text` is provided.

## Usage

```python
from consultation_layer import ConsultationEngine, consultation_input_from_unified_report

engine = ConsultationEngine()
payload = engine.consult_json(
    consultation_input_from_unified_report(
        unified_report,
        problem_text="No marriage till age 38",
        client_id="client-001",
    )
)
```

## Output Contract

Top-level keys:

- `consultation_id`
- `analyzed_at`
- `problem_text`
- `specialist_agents` — 4 specialist agent outputs
- `senior_guru` — final synthesis
- `self_review` — quality review with 0–100 score
- `audit_trail` — full trace of rule/engine sources
- `metadata`

Flags:

- `metadata.ai_prediction`: `false`
- `metadata.marketing_text`: `false`
- `metadata.engine`: `consultation_layer_v1`

Every agent finding includes an `audit` array with `rule_source`, `engine_source`, and `reason_used`.

## Integration

- **ReportService** — adds `consultation` to the dashboard report response
- **ClientHistoryStore** — records `consultation` entries when `client_id` is provided

## Tests

```bash
python -m pytest tests/unit/test_consultation_layer.py -v
```

## Design Principles

1. **Structured JSON only** — no narrative prediction or marketing language
2. **Evidence-backed** — every finding links to engine output or knowledge rule
3. **Auditable** — full audit trail across all agents
4. **Self-reviewed** — quality score penalizes contradictions, missing evidence, and weak remedies
