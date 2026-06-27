"""Client history analysis engine."""

from __future__ import annotations

from collections import Counter

from reasoning_layer.history.store import ClientHistoryStore
from reasoning_layer.types import ClientHistoryInsight, ClientHistoryRecord


def analyze_client_history(
    store: ClientHistoryStore,
    client_id: str | None,
) -> ClientHistoryInsight | None:
    if not client_id:
        return None

    records = store.records_for_client(client_id)
    if not records:
        return ClientHistoryInsight(
            repeated_problems=(),
            remedy_effectiveness=(),
            detected_patterns=(),
            consultation_count=0,
            report_count=0,
        )

    domain_counts: Counter[str] = Counter()
    for record in records:
        if record.problem_domain:
            domain_counts[record.problem_domain] += 1

    repeated = tuple(domain for domain, count in domain_counts.items() if count >= 2)

    remedy_records = store.remedies_for_client(client_id)
    effectiveness: list[dict[str, object]] = []
    for record in remedy_records:
        effectiveness.append(
            {
                "remedies": list(record.remedies_applied),
                "outcome": record.outcome or "unknown",
                "recorded_at": record.recorded_at.isoformat(),
            }
        )

    patterns: list[dict[str, object]] = []
    if repeated:
        patterns.append(
            {
                "pattern_type": "repeated_domain",
                "domains": list(repeated),
                "occurrence_threshold": 2,
            }
        )

    unresolved = [
        record.problem_domain
        for record in records
        if record.record_type == "report" and record.outcome in {None, "unresolved", "partial"}
    ]
    if len(unresolved) >= 2:
        patterns.append(
            {
                "pattern_type": "persistent_unresolved",
                "domains": list(dict.fromkeys(d for d in unresolved if d)),
                "count": len(unresolved),
            }
        )

    return ClientHistoryInsight(
        repeated_problems=repeated,
        remedy_effectiveness=tuple(effectiveness),
        detected_patterns=tuple(patterns),
        consultation_count=len(store.consultations_for_client(client_id)),
        report_count=len(store.reports_for_client(client_id)),
    )
