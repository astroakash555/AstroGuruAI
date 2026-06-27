"""Rule studio constants."""

from __future__ import annotations

RULE_SYSTEMS = ("vedic", "lal_kitab", "kp", "remedy")

RULE_STATUSES = (
    "draft",
    "pending_review",
    "approved",
    "active",
    "inactive",
    "rejected",
)

APPROVAL_ACTIONS = ("submit", "approve", "reject", "activate", "deactivate")

DOMAINS = ("marriage", "career", "health", "finance", "general")

CONFLICT_OVERLAP_THRESHOLD = 0.6

SANDBOX_PASS_THRESHOLD = 0.5

PERFORMANCE_TRACKING_WINDOW = 50
