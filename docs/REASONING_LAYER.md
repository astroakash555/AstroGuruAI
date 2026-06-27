# Reasoning Layer

Professional multi-system astrology reasoning for AstroGuruAI. Produces structured JSON only — no prediction prose and no AI storytelling.

## Architecture

```
reasoning_layer/
├── engine.py                 # ReasoningEngine orchestrator
├── types.py                  # Typed input/output models
├── constants.py              # Stances, domains, system names
├── synthesizers/
│   └── system_signals.py     # Normalize Vedic/KP/LK/Dasha/Transit/KB signals
├── engines/
│   ├── root_cause.py         # Actual, secondary, hidden causes
│   ├── contradiction.py      # Cross-system opposing evidence
│   ├── confidence.py         # 0–100 confidence scoring
│   └── consensus.py          # Multi-system agreement/disagreement
├── history/
│   ├── store.py              # Client report/remedy/consultation storage
│   └── analyzer.py           # Repeated problems, remedy effectiveness
├── audit/
│   └── trail.py              # Rule source + engine source + reason audit
└── serializers/
    ├── schemas.py            # Pydantic JSON contract
    └── serializer.py         # to_json_dict / to_json_string
```

## Pipeline Position

```
ReportOrchestrator
  → Vedic / Dasha / Transit / Lal Kitab / KP / Problem / Astro Intelligence
  → ReasoningEngine
  → Unified Report JSON (reasoning section)
```

## Engines

### Root Cause Engine

Detects three cause tiers from chart, dasha, transit, and intelligence data:

| Field | Description |
|-------|-------------|
| `cause_type` | `actual`, `secondary`, `hidden` |
| `triggering_planet` | Primary planet driving the outcome |
| `supporting_planet` | Secondary influencing planet |
| `dasha_influence` | Active period lords and influence type |
| `transit_influence` | Blocking/supporting transit impacts |
| `audit` | Traceable rule and engine sources |

Example problem: *"No marriage till age 38"* → actual cause from Saturn/Mars dosha stack, secondary from dasha delay, hidden from Lal Kitab dosh or Saturn transit block.

### Contradiction Engine

Compares normalized system stances (`support`, `block`, `delay`, `neutral`) and emits contradictions when systems disagree:

```json
{
  "topic": "marriage:vedic_vs_kp",
  "supporting_evidence": [{"system": "vedic", "stance": "support", "strength": 0.6}],
  "opposing_evidence": [{"system": "kp", "stance": "delay", "strength": 0.4}],
  "confidence_score": 60.0
}
```

### Confidence Engine

Produces a 0–100 `overall_score` from weighted agreement:

| Component | Weight |
|-----------|--------|
| Vedic | 25% |
| KP | 20% |
| Lal Kitab | 15% |
| Dasha | 20% |
| Transit | 20% |

Contradictions apply a penalty; cross-system consensus adds a bonus.

### Multi-System Consensus Engine

Compares Vedic, KP, and Lal Kitab stances and resolves:

- `agreement_areas` — aligned system signals
- `disagreement_areas` — conflicting signals
- `final_consensus` — e.g. `delayed_outcome`, `blocked_outcome`, `mixed_signals`

### Client History Engine

JSON-backed store tracks:

- Previous reports
- Previous remedies
- Previous consultations

Analyzes repeated problem domains, remedy effectiveness, and persistent unresolved patterns.

### Audit Engine

Every conclusion includes:

```json
{
  "rule_source": "doshas_engine",
  "engine_source": "root_cause_engine",
  "reason_used": "actual cause: Saturn in dosha mangal_dosha",
  "reference_id": "mangal_dosha"
}
```

The full `audit_trail` aggregates all entries. `metadata.audit_validation_errors` is empty when coverage is complete.

## Usage

```python
from reasoning_layer import ReasoningEngine, ReasoningInput

engine = ReasoningEngine()
result = engine.analyze(reasoning_input)
payload = engine.analyze_json(reasoning_input)
```

From a unified report:

```python
from reasoning_layer import ReasoningEngine, reasoning_input_from_unified_report

engine = ReasoningEngine()
reasoning_input = reasoning_input_from_unified_report(unified_report, problem_text="No marriage till age 38")
payload = engine.analyze_json(reasoning_input)
```

## Output Contract

Top-level JSON keys:

- `analyzed_at`
- `problem_domain`
- `root_causes`
- `contradictions`
- `confidence`
- `consensus`
- `client_history`
- `audit_trail`
- `metadata`

Flags:

- `metadata.ai_prediction`: `false`
- `metadata.ai_storytelling`: `false`
- `metadata.engine`: `reasoning_layer_v1`

## Tests

```bash
python -m pytest tests/unit/test_reasoning_layer.py -v
```

## Integration

`ReportOrchestrator` automatically runs `ReasoningEngine` after astro intelligence and adds a `reasoning` section to the unified report. Client reports are recorded in the history store when `client_id` is provided.
