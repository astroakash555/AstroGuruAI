"""Pydantic schemas for knowledge search JSON."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class KnowledgeSearchJSON(BaseSchema):
    queried_at: datetime
    query: dict[str, Any]
    ranked_rules: list[dict[str, Any]]
    matched_entities: list[dict[str, Any]]
    summary: dict[str, Any]
    metadata: dict[str, object]
