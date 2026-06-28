"""Typed models for premium PDF generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PDFBuildInput:
    """Input payload for premium PDF rendering."""

    client_report_json: dict[str, Any]
    unified_report_json: dict[str, Any] | None = None
    report_id: str | None = None
    client_name: str | None = None
    online_report_url: str | None = None
    ai_chat_url: str | None = None
    file_prefix: str = "astroguru_report"


@dataclass(frozen=True)
class PDFBuildResult:
    """Result of a premium PDF build."""

    file_path: str
    file_name: str
    file_size_bytes: int
    generated_at: datetime
    page_count: int = 0
    section_pages: dict[str, int] = field(default_factory=dict)
