from trading.config import AppConfig
from trading.infra.anthropic_client import AnthropicRouter, StrategyAsset


def test_prompt_hierarchy_and_assets():
    router = AnthropicRouter(AppConfig(raw={"models": {"strategy_director": "claude-4-6-opus-latest"}, "anthropic": {"thinking": "adaptive"}}))
    assets = [
        StrategyAsset(symbol="AAPL", status="current_holding", features={"k": 1}),
        StrategyAsset(symbol="NVDA", status="watchlist", features={"k": 2}),
    ]
    prompt = router.compile_strategy_director_prompt(global_portfolio_state={"cash": 1000}, assets=assets)
    assert "<global_portfolio_state>" in prompt
    assert "<market_data>" in prompt
    assert prompt.count("<asset>") == 2
    assert "<symbol>AAPL</symbol>" in prompt
    assert "<status>watchlist</status>" in prompt
    assert "<instructions>" in prompt
