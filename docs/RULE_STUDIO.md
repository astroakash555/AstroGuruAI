# Expert Rule Authoring Studio

No-code rule management for AstroGuruAI experts. Create, version, test, approve, and track custom astrology rules across Vedic, Lal Kitab, KP, and Remedy systems.

## Architecture

```
rule_studio/
├── engine.py                 # RuleStudioEngine orchestrator
├── types.py                  # ExpertRule, RuleConflict, SandboxTestResult
├── constants.py              # Systems, statuses, thresholds
├── store/repository.py       # JSON CRUD + versioning
├── validators/
│   ├── schema_validator.py   # Field validation
│   └── conflict_detector.py  # Overlapping rule conflicts
├── sandbox/tester.py         # Rule testing sandbox
├── workflow/approval.py      # Draft → review → approve → activate
├── performance/tracker.py    # Sandbox performance tracking
└── serializers/              # Pydantic JSON contracts

rule_studio_data/             # Persisted expert rules (JSON)
backend/app/api/v1/endpoints/rule_studio.py
```

## Rule Structure (JSON)

```json
{
  "rule_id": "vedic_saturn_7th_delay",
  "rule_name": "Saturn 7th House Marriage Delay",
  "system": "vedic",
  "description": "Saturn in 7th house delays marriage.",
  "conditions": {
    "planets": ["Saturn", "Mars"],
    "houses": [7, 8],
    "dasha_lords": ["Saturn"],
    "transits": ["sade_sati_phase"],
    "tags": ["marriage", "delay"]
  },
  "weight": 0.8,
  "confidence": 0.75,
  "outcome": "delayed_outcome",
  "source_book": "Brihat Parashara Hora Shastra",
  "notes": "Classical delay indicator.",
  "domain": "marriage",
  "category": "delayed_marriage",
  "version": 1,
  "status": "draft",
  "is_active": false
}
```

## Supported Systems

| System | Use Case |
|--------|----------|
| `vedic` | Domain rules, yogas, doshas |
| `lal_kitab` | Rin, dosh, planet-house protocols |
| `kp` | Event timing, significator chains |
| `remedy` | Remedy selection rules |

## Features

### 1. Rule Management
Create, read, update expert rules via API or `RuleStudioEngine`.

### 2. Rule Versioning
Every update increments `version` and stores a snapshot in `rule_studio_data/versions/`.

### 3. Activation / Deactivation
Approved rules can be activated (`is_active: true`) or deactivated without deletion.

### 4. Conflict Detection
Detects overlapping conditions with conflicting outcomes among active/approved rules.

### 5. Testing Sandbox
Test rules against sample chart context. Returns matched/unmatched conditions and match score.

### 6. Approval Workflow
```
POST /rules/{id}/submit   → pending_review
POST /rules/{id}/approve → approved
POST /rules/{id}/reject   → rejected
POST /rules/{id}/activate → active
POST /rules/{id}/deactivate → inactive
```

### 7. Performance Tracking
Sandbox runs recorded with pass rate and average match score per rule.

## API Reference

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/rule-studio/manifest` | Rule counts by system/status |
| GET | `/rule-studio/report` | Studio summary report |
| GET | `/rule-studio/rules` | List rules (filter by system, status) |
| GET | `/rule-studio/rules/{id}` | Rule detail + versions + performance |
| POST | `/rule-studio/rules` | Create rule |
| PATCH | `/rule-studio/rules/{id}` | Update rule (increments version) |
| POST | `/rule-studio/rules/{id}/submit` | Submit for review |
| POST | `/rule-studio/rules/{id}/approve` | Approve rule |
| POST | `/rule-studio/rules/{id}/reject` | Reject rule |
| POST | `/rule-studio/rules/{id}/activate` | Activate rule |
| POST | `/rule-studio/rules/{id}/deactivate` | Deactivate rule |
| GET | `/rule-studio/conflicts` | Detect conflicts |
| POST | `/rule-studio/rules/{id}/sandbox` | Test in sandbox |

## Python Usage

```python
from rule_studio import RuleStudioEngine

engine = RuleStudioEngine("rule_studio_data")
result = engine.create_rule_json({
    "rule_name": "Mars 8th House Surgery Risk",
    "system": "vedic",
    "description": "Mars in 8th indicates surgery risk.",
    "conditions": {"planets": ["Mars"], "houses": [6, 8]},
    "weight": 0.7,
    "confidence": 0.65,
    "outcome": "blocked_outcome",
    "source_book": "Phaladeepika",
    "domain": "health",
})
```

## Configuration

```env
RULE_STUDIO_DATA_PATH=rule_studio_data
```

## Tests

```bash
python -m pytest tests/unit/test_rule_studio.py -v
python -m pytest tests/integration/test_rule_studio_api.py -v
```

## Design Principles

1. **JSON only** — no narrative predictions in rule studio output
2. **No coding required** — experts author rules via structured fields
3. **Versioned and auditable** — full approval history and version snapshots
4. **Test before activate** — sandbox validates conditions against sample charts
5. **Performance tracked** — sandbox pass rates inform rule quality
