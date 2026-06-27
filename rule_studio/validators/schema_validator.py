"""Rule schema validation."""

from __future__ import annotations

from typing import Any

from rule_studio.constants import DOMAINS, RULE_SYSTEMS


def validate_rule_payload(payload: dict[str, Any], *, partial: bool = False) -> tuple[str, ...]:
    errors: list[str] = []

    if not partial:
        required = ["rule_name", "system", "outcome", "description", "conditions", "weight", "confidence", "source_book"]
        for field in required:
            if field not in payload or payload[field] in (None, ""):
                errors.append(f"missing_field:{field}")
    else:
        for field in ("rule_name", "system", "outcome", "description", "source_book"):
            if field in payload and payload[field] in (None, ""):
                errors.append(f"missing_field:{field}")

    system = payload.get("system")
    if system and system not in RULE_SYSTEMS:
        errors.append(f"invalid_system:{system}")

    domain = payload.get("domain")
    if domain and domain not in DOMAINS:
        errors.append(f"invalid_domain:{domain}")

    weight = payload.get("weight")
    if weight is not None and not 0.0 <= float(weight) <= 1.0:
        errors.append("invalid_weight:must_be_0_to_1")

    confidence = payload.get("confidence")
    if confidence is not None and not 0.0 <= float(confidence) <= 1.0:
        errors.append("invalid_confidence:must_be_0_to_1")

    conditions = payload.get("conditions")
    if conditions is not None and not isinstance(conditions, dict):
        errors.append("invalid_conditions:must_be_object")

    return tuple(errors)
