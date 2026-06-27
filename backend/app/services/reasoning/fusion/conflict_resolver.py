"""Cross-engine conflict detection for fused intelligence."""

from __future__ import annotations

from backend.app.services.reasoning.fusion.models import FusionEngineId, InterpretationConflict, NormalizedObservation

CONFLICT_SEVERITY_THRESHOLD = 0.25
CONFLICT_CONFIDENCE_THRESHOLD = 0.70


def detect_conflicts(
    observations: tuple[NormalizedObservation, ...],
) -> tuple[InterpretationConflict, ...]:
    """
    Detect conflicting interpretations across intelligence engines.

    Conflicts arise when different engines produce high-confidence observations
    about the same planetary or house focus with materially different severity.
    """
    grouped: dict[tuple[frozenset[str], frozenset[int]], list[NormalizedObservation]] = {}

    for observation in observations:
        if not observation.affected_planets and not observation.affected_houses:
            continue
        focus_key = (frozenset(observation.affected_planets), frozenset(observation.affected_houses))
        grouped.setdefault(focus_key, []).append(observation)

    conflicts: list[InterpretationConflict] = []
    conflict_index = 0

    for (planets, houses), group in sorted(grouped.items(), key=_group_sort_key):
        engines = {item.engine for item in group}
        if len(engines) < 2:
            continue

        high_confidence = [
            item for item in group if item.confidence >= CONFLICT_CONFIDENCE_THRESHOLD
        ]
        if len(high_confidence) < 2:
            continue

        severities = [item.severity for item in high_confidence]
        severity_spread = max(severities) - min(severities)
        if severity_spread < CONFLICT_SEVERITY_THRESHOLD:
            continue

        conflict_index += 1
        engine_tuple = tuple(sorted({item.engine for item in high_confidence}, key=lambda e: e.value))
        observation_ids = tuple(dict.fromkeys(item.observation_id for item in high_confidence))
        strongest = max(high_confidence, key=lambda item: item.severity)
        weakest = min(high_confidence, key=lambda item: item.severity)

        conflicts.append(
            InterpretationConflict(
                conflict_id=f"fusion-conflict-{conflict_index:04d}",
                title=_conflict_title(planets, houses),
                explanation=(
                    f"Engines disagree on focus { _format_focus(planets, houses) }: "
                    f"{strongest.engine.value} reports severity {strongest.severity:.2f} "
                    f"({strongest.title}), while {weakest.engine.value} reports "
                    f"{weakest.severity:.2f} ({weakest.title})."
                ),
                engines=engine_tuple,
                observation_ids=observation_ids,
                affected_planets=tuple(sorted(planets)),
                affected_houses=tuple(sorted(houses)),
                severity_spread=round(severity_spread, 4),
                confidence=round(
                    sum(item.confidence for item in high_confidence) / len(high_confidence),
                    4,
                ),
            )
        )

    return tuple(conflicts)


def conflict_observation_ids(
    conflicts: tuple[InterpretationConflict, ...],
) -> frozenset[str]:
    """Return all source observation identifiers involved in conflicts."""
    ids: set[str] = set()
    for conflict in conflicts:
        ids.update(conflict.observation_ids)
    return frozenset(ids)


def _group_sort_key(
    item: tuple[tuple[frozenset[str], frozenset[int]], list[NormalizedObservation]],
) -> tuple[str, int]:
    planets, houses = item[0]
    planet_key = ",".join(sorted(planets))
    house_key = min(houses) if houses else 0
    return planet_key, house_key


def _conflict_title(planets: frozenset[str], houses: frozenset[int]) -> str:
    """Build a concise title for a detected conflict."""
    if planets and houses:
        return (
            f"Conflicting Interpretations for {', '.join(sorted(planets))} "
            f"and Houses {', '.join(str(house) for house in sorted(houses))}"
        )
    if planets:
        return f"Conflicting Interpretations for {', '.join(sorted(planets))}"
    return f"Conflicting Interpretations for Houses {', '.join(str(house) for house in sorted(houses))}"


def _format_focus(planets: frozenset[str], houses: frozenset[int]) -> str:
    """Format planets and houses for conflict explanations."""
    parts: list[str] = []
    if planets:
        parts.append(f"planets {', '.join(sorted(planets))}")
    if houses:
        parts.append(f"houses {', '.join(str(house) for house in sorted(houses))}")
    return " and ".join(parts)
