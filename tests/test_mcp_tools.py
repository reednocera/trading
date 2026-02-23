from trading.mcp.registry import tools_for_event


def test_earnings_tools_injected():
    tools = tools_for_event(earnings_window_active=True)
    assert "earnings_analysis_skill" in tools
