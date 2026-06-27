# Case Learning Engine

Learn from real client consultations to improve predictions, remedies, and rules over time.

## Architecture

```
case_learning/
├── engine.py                 # CaseLearningEngine orchestrator
├── types.py                  # ConsultationCase, LearningMetrics, RuleSuggestion
├── constants.py              # Categories, thresholds
├── store/repository.py         # JSON case storage
├── metrics/calculator.py       # Prediction/remedy/rule accuracy
├── analyzers/
│   ├── suggestions.py          # Rule improvements, candidates, weak/obsolete
│   └── feedback.py             # Feedback loop builder
├── reports/generator.py        # Learning report generator
└── serializers/                # Pydantic JSON contracts
```

## Stored Case Data

Each consultation case records:

| Field | Description |
|-------|-------------|
| `problem_text` | Client problem |
| `kundali_snapshot` | Chart at consultation time |
| `system_prediction` | Engine prediction snapshot |
| `applied_rules` | Rules used during consultation |
| `applied_remedies` | Remedies prescribed |
| `predicted_outcome` | System consensus outcome |
| `final_outcome` | Actual life outcome |
| `follow_up_results` | Follow-up visits and remedy effectiveness |

## Tracked Categories

- `marriage`
- `career`
- `health`
- `finance`
- `court_case`

## Metrics

| Metric | Measures |
|--------|----------|
| `prediction_accuracy` | Predicted vs final outcome alignment |
| `remedy_success_rate` | Follow-up remedy effectiveness |
| `rule_accuracy` | Applied rules vs actual outcome |

## Automatic Suggestions

| Type | Trigger |
|------|---------|
| `rule_improvement` | Rule accuracy 45–70% |
| `new_rule_candidate` | Cases without matching rules (pattern extraction) |
| `weak_rule` | Rule accuracy below 45% |
| `obsolete_rule` | Rule accuracy below 25% with repeated use |

## Feedback Loops

Cases → metrics → suggestions → target modules:

- `reasoning_layer` — low prediction accuracy
- `remedy_engine` — low remedy success
- `rule_studio` — low rule accuracy / new candidates
- `knowledge_brain` — category underperformance

## API Reference

Base: `/api/v1/case-learning`

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/manifest` | Case counts by category |
| POST | `/cases` | Record consultation case |
| POST | `/cases/from-report` | Record from unified report |
| GET | `/cases` | List cases |
| GET | `/cases/{id}` | Get case |
| POST | `/cases/{id}/follow-up` | Add follow-up result |
| GET | `/metrics` | Learning metrics |
| GET | `/suggestions` | Rule suggestions |
| GET | `/feedback-loops` | Feedback loops |
| GET | `/report` | Full learning report |

## Python Usage

```python
from case_learning import CaseLearningEngine

engine = CaseLearningEngine("case_learning_data")
engine.record_consultation_json({
    "client_id": "client-001",
    "category": "marriage",
    "problem_text": "No marriage till age 38",
    "kundali_snapshot": {...},
    "system_prediction": {"consensus_outcome": "delayed_outcome"},
    "applied_rules": ["marriage_delay_saturn"],
    "applied_remedies": ["saturn_mantra"],
    "predicted_outcome": "delayed_outcome",
    "final_outcome": "delayed_outcome",
})
report = engine.learning_report_json()
```

## Configuration

```env
CASE_LEARNING_DATA_PATH=case_learning_data
```

## Tests

```bash
python -m pytest tests/unit/test_case_learning.py -v
python -m pytest tests/integration/test_case_learning_api.py -v
```

## Integration with Other Engines

| Engine | Integration |
|--------|-------------|
| `consultation_layer` | Record cases after consultation |
| `rule_studio` | Apply suggestions as new/updated rules |
| `validation_framework` | Cross-validate learned patterns |
| `reasoning_layer` | Client history informs learning |

## Design Principles

1. **JSON only** — no narrative predictions in learning output
2. **Real consultations** — learn from actual client outcomes
3. **Closed feedback loops** — metrics drive actionable suggestions
4. **Category tracking** — per-domain accuracy monitoring
5. **Follow-up aware** — remedy success measured over time
