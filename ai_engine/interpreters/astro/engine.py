"""Astro interpretation engine."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from ai_engine.core.base import PromptContext
from ai_engine.interpreters.astro.fallback import build_fallback_interpretation
from ai_engine.interpreters.astro.serializer import to_json_dict
from ai_engine.interpreters.astro.types import AstroInterpretationInput, AstroInterpretationResult
from ai_engine.prompts.loader import PromptLoader
from ai_engine.providers.gemini.client import GeminiClient


class AstroInterpretationEngine:
    """Generate professional astrology explanations from unified report JSON."""

    REQUIRED_KEYS = (
        "root_cause_explanation",
        "affected_planets_explanation",
        "affected_houses_explanation",
        "dasha_impact_explanation",
        "transit_impact_explanation",
        "kp_findings_explanation",
        "lal_kitab_findings_explanation",
        "summary",
    )

    def __init__(
        self,
        gemini_client: GeminiClient | None = None,
        prompt_loader: PromptLoader | None = None,
    ) -> None:
        self._gemini = gemini_client or GeminiClient.from_env()
        self._prompts = prompt_loader or PromptLoader()

    async def interpret(self, interpretation_input: AstroInterpretationInput) -> AstroInterpretationResult:
        if self._gemini.is_available:
            payload = await self._interpret_with_gemini(interpretation_input)
            source = "gemini"
        else:
            payload = build_fallback_interpretation(interpretation_input.report_json)
            source = "rule_based_fallback"

        return AstroInterpretationResult(
            generated_at=datetime.now(timezone.utc),
            root_cause_explanation=payload["root_cause_explanation"],
            affected_planets_explanation=payload["affected_planets_explanation"],
            affected_houses_explanation=payload["affected_houses_explanation"],
            dasha_impact_explanation=payload["dasha_impact_explanation"],
            transit_impact_explanation=payload["transit_impact_explanation"],
            kp_findings_explanation=payload["kp_findings_explanation"],
            lal_kitab_findings_explanation=payload["lal_kitab_findings_explanation"],
            summary=payload["summary"],
            metadata={
                "engine": "astro_interpretation_v1",
                "source": source,
                "locale": interpretation_input.locale,
            },
        )

    async def interpret_json(self, interpretation_input: AstroInterpretationInput) -> dict[str, Any]:
        return to_json_dict(await self.interpret(interpretation_input))

    async def _interpret_with_gemini(
        self,
        interpretation_input: AstroInterpretationInput,
    ) -> dict[str, str]:
        system_prompt = self._prompts.load("astro_interpretation", "system.txt")
        user_template = self._prompts.load("astro_interpretation", "user.txt")
        user_prompt = self._prompts.render(
            user_template,
            report_json=json.dumps(interpretation_input.report_json, ensure_ascii=False),
        )
        return await self._gemini.generate_json(
            PromptContext(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={"task": "astro_interpretation"},
            ),
            required_keys=self.REQUIRED_KEYS,
        )
