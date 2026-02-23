from __future__ import annotations

from trading.agents.director import StrategyDirector
from trading.config import load_config
from trading.core.scheduler import AdaptiveInputs, AdaptiveIntervalScheduler
from trading.infra.anthropic_client import AnthropicRouter, StrategyAsset
from trading.mcp.registry import tools_for_event


def implementation_plan() -> dict:
    cfg = load_config()
    universe_size = len(cfg.universe.get("holdings", [])) + len(cfg.universe.get("watchlist", []))
    return {
        "llm_stack": "Anthropic Claude 4.5/4.6 routing",
        "state": "Postgres via SQLAlchemy async",
        "mcp": "single multiplexed local MCP server",
        "self_heal": "haiku repair retry up to 2 attempts",
        "strategy_batching": f"single Opus call across {universe_size} configured assets",
    }


def _batched_assets_from_config() -> list[StrategyAsset]:
    cfg = load_config()
    holdings = cfg.universe.get("holdings", [])
    watchlist = cfg.universe.get("watchlist", [])
    symbols = [(s, "holding") for s in holdings] + [(s, "watchlist") for s in watchlist]
    return [
        StrategyAsset(
            symbol=symbol,
            status=status,
            features={"momentum_20d": 0.0, "iv_rank": 50},
        )
        for symbol, status in symbols
    ]


def run_decision() -> dict:
    config = load_config()
    router = AnthropicRouter(config)
    window = config.events.get("earnings_window_days", {"start": -1, "end": 2})
    earnings_window_active = int(window.get("start", -1)) <= 0 <= int(window.get("end", 2))
    tools = tools_for_event(earnings_window_active=earnings_window_active)
    director = StrategyDirector(router=router)
    payload = director.build_batched_prompt(
        system_rules="Apply risk limits, gating, and portfolio improvement test.",
        global_portfolio_state={
            "cash": 150000,
            "gross_exposure": 1.1,
            "net_exposure": 0.22,
            "daily_turnover_used_pct": 0.14,
        },
        assets=_batched_assets_from_config(),
    )
    payload["tools"] = [{"name": name} for name in tools]
    print("[DECISION_LOG] built single batched Strategy Director payload from configured universe")
    return payload


def run_schedule_probe() -> int:
    config = load_config()
    scheduler = AdaptiveIntervalScheduler(config=config)
    interval = scheduler.next_interval_minutes(
        AdaptiveInputs(event_velocity=0.4, volatility_state="normal", quota_pressure=0.1)
    )
    print(f"[DECISION_LOG] adaptive interval={interval}m windows={scheduler.windows()}")
    return interval
