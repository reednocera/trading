from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MCPToolSpec:
    name: str
    enabled: bool


DEFAULT_TOOLS = [
    MCPToolSpec(name="yahoo_quotes", enabled=True),
    MCPToolSpec(name="finnhub_data", enabled=True),
    MCPToolSpec(name="fmp_data", enabled=True),
    MCPToolSpec(name="composio_postgres", enabled=True),
    MCPToolSpec(name="composio_root_cause_tracing", enabled=True),
    MCPToolSpec(name="composio_csv_summarizer", enabled=True),
]


def tools_for_event(*, earnings_window_active: bool) -> list[str]:
    tools = [t.name for t in DEFAULT_TOOLS if t.enabled]
    if earnings_window_active:
        tools.extend(["earnings_analysis_skill", "comparable_company_analysis_skill"])
    return tools
