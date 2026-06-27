"""Naming suggestion engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from astrology_engine.core.constants import SIGN_NAMES_EN
from naming_engine.constants import GENDER_SUFFIXES, NAKSHATRA_PADA_SYLLABLES, RASHI_NAME_PREFIXES
from naming_engine.schemas import NamingJSON
from naming_engine.types import NameSuggestion, NamingInput, NamingResult


class NamingEngine:
    """Generate name suggestions from nakshatra, pada, and rashi."""

    def suggest(self, naming_input: NamingInput) -> NamingResult:
        syllables = NAKSHATRA_PADA_SYLLABLES.get(
            (naming_input.nakshatra, naming_input.pada),
            ("Sa", "Ra", "Vi", "Dev"),
        )
        rashi_prefixes = RASHI_NAME_PREFIXES.get(naming_input.rashi_sign_index, ("Astro",))
        suffixes = GENDER_SUFFIXES.get(naming_input.gender, GENDER_SUFFIXES["neutral"])
        rashi_name = SIGN_NAMES_EN[naming_input.rashi_sign_index]

        suggestions: list[NameSuggestion] = []
        for index, syllable in enumerate(syllables):
            for prefix in rashi_prefixes[:2]:
                for suffix in suffixes[:2]:
                    name = f"{prefix}{syllable}{suffix}".capitalize()
                    suggestions.append(
                        NameSuggestion(
                            name=name,
                            syllable_seed=syllable,
                            nakshatra=naming_input.nakshatra,
                            pada=naming_input.pada,
                            rashi=rashi_name,
                            score=round(0.9 - index * 0.05, 3),
                            reasoning=(
                                f"Derived from {naming_input.nakshatra} pada {naming_input.pada} "
                                f"syllable '{syllable}' and {rashi_name} rashi influence."
                            ),
                        )
                    )

        unique: dict[str, NameSuggestion] = {}
        for item in sorted(suggestions, key=lambda entry: entry.score, reverse=True):
            unique.setdefault(item.name, item)
        final = tuple(list(unique.values())[: naming_input.count])

        return NamingResult(
            generated_at=datetime.now(timezone.utc),
            suggestions=final,
            metadata={"engine": "naming_engine_v1", "gender": naming_input.gender},
        )

    def suggest_json(self, naming_input: NamingInput) -> dict[str, Any]:
        result = self.suggest(naming_input)
        payload = NamingJSON(
            generated_at=result.generated_at,
            suggestions=[
                {
                    "name": item.name,
                    "syllable_seed": item.syllable_seed,
                    "nakshatra": item.nakshatra,
                    "pada": item.pada,
                    "rashi": item.rashi,
                    "score": item.score,
                    "reasoning": item.reasoning,
                }
                for item in result.suggestions
            ],
            metadata=dict(result.metadata),
        )
        return payload.model_dump(mode="json")
