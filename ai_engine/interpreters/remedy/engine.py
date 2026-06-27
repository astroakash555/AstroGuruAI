"""Remedy generation engine."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from ai_engine.core.base import PromptContext
from ai_engine.interpreters.remedy.fallback import build_fallback_remedies
from ai_engine.interpreters.remedy.serializer import to_json_dict
from ai_engine.interpreters.remedy.types import GeneratedRemedy, RemedyGenerationInput, RemedyGenerationResult
from ai_engine.prompts.loader import PromptLoader
from ai_engine.providers.gemini.client import GeminiClient


class RemedyGenerationEngine:
    """Generate prioritized remedies across Vedic, Lal Kitab, and KP systems."""

    def __init__(
        self,
        gemini_client: GeminiClient | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self._gemini = gemini_client or GeminiClient.from_env()
        self._prompts = prompt_loader or PromptLoader()

    async def generate(self, generation_input: RemedyGenerationInput) -> RemedyGenerationResult:
        if self._gemini.is_available:
            payload = await self._generate_with_gemini(generation_input)
            remedies = _parse_gemini_remedies(payload.get("remedies", []))
            summary = payload.get("summary", "Gemini-generated remedy plan.")
            source = "gemini"
        else:
            remedies = build_fallback_remedies(
                generation_input.report_json,
                max_remedies=generation_input.max_remedies,
            )
            summary = f"Generated {len(remedies)} prioritized remedies from structured knowledge base."
            source = "rule_based_fallback"

        return RemedyGenerationResult(
            generated_at=datetime.now(timezone.utc),
            remedies=remedies,
            summary=summary,
            metadata={"engine": "remedy_generation_v1", "source": source},
        )

    async def generate_json(self, generation_input: RemedyGenerationInput) -> dict[str, Any]:
        return to_json_dict(await self.generate(generation_input))

    async def _generate_with_gemini(self, generation_input: RemedyGenerationInput) -> dict[str, Any]:
        system_prompt = self._prompts.load("remedy_generation", "system.txt")
        user_template = self._prompts.load("remedy_generation", "user.txt")
        user_prompt = self._prompts.render(
            user_template,
            report_json=json.dumps(generation_input.report_json, ensure_ascii=False),
        )
        return await self._gemini.generate_json(
            PromptContext(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={"task": "remedy_generation"},
            ),
            required_keys=("remedies", "summary"),
        )


def _parse_gemini_remedies(items: list[dict[str, Any]]) -> tuple[GeneratedRemedy, ...]:
    remedies: list[GeneratedRemedy] = []
    for item in items:
        remedies.append(
            GeneratedRemedy(
                remedy_type=str(item.get("remedy_type", "behavioral")),
                astrology_system=str(item.get("astrology_system", "vedic")),
                title=str(item.get("title", "Remedy")),
                description=str(item.get("description", "")),
                planet=item.get("planet"),
                house=item.get("house"),
                priority=int(item.get("priority", 3)),
                confidence_score=float(item.get("confidence_score", 0.6)),
                expected_effect=str(item.get("expected_effect", item.get("description", ""))),
            )
        )
    remedies.sort(key=lambda remedy: (remedy.priority, -remedy.confidence_score))
    return tuple(remedies)
