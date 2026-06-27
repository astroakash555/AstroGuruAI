"""Prompt template loader."""

from __future__ import annotations

from pathlib import Path


class PromptLoader:
    """Load prompt templates from the prompts directory."""

    def __init__(self, prompts_path: str | Path = "prompts") -> None:
        self._root = Path(prompts_path)

    def load(self, *parts: str) -> str:
        path = self._root.joinpath(*parts)
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        return path.read_text(encoding="utf-8").strip()

    def render(self, template: str, **variables: str) -> str:
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    def load_and_render(self, *parts: str, **variables: str) -> str:
        return self.render(self.load(*parts), **variables)
