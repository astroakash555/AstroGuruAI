# Validation and Benchmarking Framework

Structured validation and benchmarking for AstroGuruAI. Compares actual life outcomes against system predictions and produces JSON-only validation reports.

## Architecture

```
validation_framework/
├── engine.py                    # ValidationEngine orchestrator
├── types.py                     # CaseStudy, ValidationReport, AccuracyMetrics
├── constants.py                 # Categories, thresholds, retraining map
├── case_validation/
│   └── validator.py             # Single case validation module
├── metrics/
│   ├── comparison.py            # Extract system prediction from unified report
│   └── accuracy.py              # Planet/house/dasha/transit/remedy accuracy
├── datasets/
│   ├── builder.py               # Build benchmark JSON datasets
│   └── loader.py                # Load benchmark case studies
├── reports/
│   └── generator.py             # Validation report generator
├── failed_cases/
│   └── store.py                 # Store failed benchmark cases
├── retraining/
│   └── recommendations.py       # Retraining recommendations
└── serializers/
    ├── schemas.py
    └── serializer.py
```

## Benchmark Categories

| Category | File |
|----------|------|
| Marriage | `benchmarks/marriage.json` |
| Divorce | `benchmarks/divorce.json` |
| Career | `benchmarks/career.json` |
| Government Job | `benchmarks/government_job.json` |
| Business | `benchmarks/business.json` |
| Health | `benchmarks/health.json` |
| Court Case | `benchmarks/court_case.json` |
| Foreign Settlement | `benchmarks/foreign_settlement.json` |
| Wealth | `benchmarks/wealth.json` |
| Raj Yoga | `benchmarks/raj_yoga.json` |

## Generate Benchmarks

```bash
python -m validation_framework.datasets.builder
```

## Usage

### Validate a single case

```python
from validation_framework import ValidationEngine
from validation_framework.case_validation.validator import case_from_dict, validate_case

result = validate_case(case_study)
```

### Run full benchmark

```python
from validation_framework import ValidationEngine

engine = ValidationEngine(
    benchmark_root="benchmarks",
    failed_cases_path="benchmarks/failed_cases.json",
)
report = engine.run_benchmark_json()
```

## Comparison Model

Each case compares:

| Field | Source |
|-------|--------|
| `actual_outcome` | Case study ground truth (real astrology case) |
| `system_prediction` | Extracted from unified report (astro_intelligence, reasoning, remedies) |
| `match_percentage` | Average of 5 accuracy metrics × 100 |

## Accuracy Metrics

| Metric | Compares |
|--------|----------|
| `planet_accuracy` | Expected vs predicted root cause planets |
| `house_accuracy` | Expected vs predicted affected houses |
| `dasha_accuracy` | Expected vs active dasha lords |
| `transit_accuracy` | Expected vs detected transit impact types |
| `remedy_accuracy` | Expected vs matched remedy IDs |

Pass threshold: `match_percentage >= 60` and each metric `>= 0.4`.

## Validation Report Output

```json
{
  "report_id": "...",
  "total_cases": 21,
  "passed_cases": 18,
  "failed_cases": 3,
  "aggregate_metrics": {
    "planet_accuracy": 0.85,
    "overall_match_percentage": 78.5
  },
  "case_results": [...],
  "failed_case_records": [...],
  "retraining_recommendations": [...],
  "metadata": {"ai_prediction": false}
}
```

## Failed Cases

Cases failing the threshold are stored in `FailedCaseStore` with:

- `case_id`, `category`, `match_percentage`
- `failed_metrics` — which accuracy metrics failed
- `case_snapshot` — actual vs predicted comparison

## Retraining Recommendations

Generated from failed metric patterns:

- Target module (e.g. `astro_intelligence`, `remedy_engine`)
- Priority (`high`, `medium`, `low`)
- Suggested action for knowledge/rule expansion

## Tests

```bash
python -m pytest tests/unit/test_validation_framework.py -v
```

## Design Principles

1. **JSON only** — no narrative predictions in validation output
2. **Real case studies** — benchmark templates based on classical astrology case patterns
3. **Auditable** — every comparison includes expected/predicted/matched detail
4. **Actionable failures** — failed cases drive retraining recommendations
