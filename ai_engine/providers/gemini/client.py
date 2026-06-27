"""Production Gemini API client."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from ai_engine.core.base import InferenceResult, PromptContext
from ai_engine.providers.gemini.config import GeminiConfig
from ai_engine.providers.gemini.cost_tracker import CostTracker
from ai_engine.providers.gemini.rate_limiter import RateLimiter
from ai_engine.providers.gemini.retry import with_retry
from ai_engine.providers.gemini.structured import extract_json_object, validate_required_keys

logger = logging.getLogger(__name__)


@dataclass
class GeminiClient:
    """Gemini provider with retry, logging, rate limiting, and cost tracking."""

    config: GeminiConfig
    cost_tracker: CostTracker = field(default_factory=CostTracker)
    rate_limiter: RateLimiter | None = None

    def __post_init__(self) -> None:
        if self.rate_limiter is None:
            self.rate_limiter = RateLimiter(self.config.requests_per_minute)

    @classmethod
    def from_env(cls) -> GeminiClient:
        config = GeminiConfig.from_env()
        return cls(config=config)

    @property
    def is_available(self) -> bool:
        return bool(self.config.enabled and self.config.api_key)

    async def generate(self, context: PromptContext, *, json_response: bool = True) -> InferenceResult:
        if not self.is_available:
            raise RuntimeError("Gemini is not enabled or API key is missing.")

        await self.rate_limiter.acquire()  # type: ignore[union-attr]

        async def _call():
            return await asyncio.to_thread(self._generate_sync, context, json_response)

        raw = await with_retry(
            _call,
            max_retries=self.config.max_retries,
            base_delay_seconds=self.config.retry_base_delay_seconds,
        )
        return raw

    async def generate_json(
        self,
        context: PromptContext,
        *,
        required_keys: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        json_context = PromptContext(
            system_prompt=(
                context.system_prompt
                + "\nRespond ONLY with valid JSON. No markdown fences or commentary."
            ),
            user_prompt=context.user_prompt,
            metadata=dict(context.metadata),
        )
        result = await self.generate(json_context)
        payload = extract_json_object(result.content)
        if required_keys:
            validate_required_keys(payload, required_keys)
        return payload

    def _generate_sync(self, context: PromptContext, json_response: bool = True) -> InferenceResult:
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai is required for Gemini integration."
            ) from exc

        genai.configure(api_key=self.config.api_key)
        model = genai.GenerativeModel(
            model_name=self.config.model,
            system_instruction=context.system_prompt,
        )
        generation_config = {
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_output_tokens,
        }
        if json_response:
            generation_config["response_mime_type"] = "application/json"

        logger.info(
            "Gemini request started model=%s metadata=%s",
            self.config.model,
            context.metadata,
        )
        response = model.generate_content(
            context.user_prompt,
            generation_config=generation_config,
        )
        text = response.text or ""
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", 0) or 0
        completion_tokens = getattr(usage, "candidates_token_count", 0) or 0
        usage_record = self.cost_tracker.record_usage(
            model=self.config.model,
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
        )
        logger.info(
            "Gemini request completed tokens=%s cost_usd=%s",
            usage_record.total_tokens,
            usage_record.estimated_cost_usd,
        )

        return InferenceResult(
            content=text,
            model=self.config.model,
            metadata={
                "provider": "gemini",
                "prompt_tokens": usage_record.prompt_tokens,
                "completion_tokens": usage_record.completion_tokens,
                "total_tokens": usage_record.total_tokens,
                "estimated_cost_usd": usage_record.estimated_cost_usd,
                "request_metadata": context.metadata,
            },
        )

    def usage_summary(self) -> dict[str, Any]:
        return {
            "total_tokens": self.cost_tracker.total_tokens,
            "total_estimated_cost_usd": self.cost_tracker.total_estimated_cost_usd,
            "request_count": len(self.cost_tracker.records),
        }
