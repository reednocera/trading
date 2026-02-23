import pytest

from trading.agents.director import PromptCompiler, StrategyDirector
from trading.config import AppConfig
from trading.infra.anthropic_client import AnthropicRouter, StrategyAsset


def _assets(n: int):
    return [StrategyAsset(symbol=f"S{i}", status="watchlist", features={"x": i}) for i in range(n)]


def test_director_requires_exactly_30_assets():
    director = StrategyDirector(router=AnthropicRouter(AppConfig(raw={})))
    with pytest.raises(ValueError):
        director.build_batched_prompt(system_rules="r", global_portfolio_state={}, assets=_assets(29))


def test_prompt_compiler_contains_required_xml_sections():
    cfg = AppConfig(raw={"risk": {"min_edge_after_cost_pct": 0.9, "min_win_prob": 0.55}})
    compiler = PromptCompiler(config=cfg)
    xml = compiler.compile_xml(system_rules="rules", global_portfolio_state={"cash": 10}, assets=_assets(30))
    assert "<system_rules>" in xml
    assert "<global_portfolio_state>" in xml
    assert "<market_data>" in xml
    assert "<instructions>" in xml
    assert xml.count("<asset>") == 30
    assert "min_edge_after_cost_pct=0.9" in xml
