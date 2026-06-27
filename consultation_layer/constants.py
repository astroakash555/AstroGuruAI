"""Consultation layer constants."""

from __future__ import annotations

AGENT_VEDIC = "vedic_astrologer"
AGENT_KP = "kp_astrologer"
AGENT_LAL_KITAB = "lal_kitab_expert"
AGENT_PROBLEM = "problem_specialist"
AGENT_SENIOR_GURU = "senior_astro_guru"
AGENT_SELF_REVIEW = "self_review_agent"

SPECIALIST_AGENTS = (
    AGENT_VEDIC,
    AGENT_KP,
    AGENT_LAL_KITAB,
    AGENT_PROBLEM,
)

WEAK_REMEDY_THRESHOLD = 0.45
MIN_REVIEW_SCORE = 0
MAX_REVIEW_SCORE = 100
