from __future__ import annotations

from typing import Any, TypedDict

from src.models import Evidence, Recommendation, ScrapeRun, Startup, StartupClassification


class PipelineState(TypedDict, total=False):
    query: str
    target_startup: str | None
    candidate_startups: list[str]
    discovered_urls: list[str]
    raw_documents: list[dict[str, Any]]
    structured_startup: Startup | None
    initial_classification: StartupClassification | None
    validated_evidences: list[Evidence]
    scrape_run: ScrapeRun | None
    rag_context: str
    recommendations: list[Recommendation]
    final_briefing: str
    errors: list[str]
    logs: list[str]
