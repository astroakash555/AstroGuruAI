# Expert Rule Authoring Studio

Structured JSON storage for custom astrology rules authored without coding.

## Rule Structure

| Field | Description |
|-------|-------------|
| `rule_id` | Unique identifier |
| `rule_name` | Human-readable name |
| `system` | `vedic`, `lal_kitab`, `kp`, `remedy` |
| `description` | Rule description |
| `conditions` | Planets, houses, dasha lords, transits, tags |
| `weight` | 0.0–1.0 scoring weight |
| `confidence` | 0.0–1.0 confidence score |
| `outcome` | Structured outcome label |
| `source_book` | Classical reference source |
| `notes` | Expert notes |

## Lifecycle

```
draft → pending_review → approved → active ↔ inactive
                      ↘ rejected
```

## API Base

`/api/v1/rule-studio`

See `docs/RULE_STUDIO.md` for full API reference.
