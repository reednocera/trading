from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AppConfig:
    raw: dict[str, Any]

    @property
    def models(self) -> dict[str, str]:
        return self.raw.get("models", {})

    @property
    def universe(self) -> dict[str, list[str]]:
        return self.raw.get("universe", {"holdings": [], "watchlist": []})

    @property
    def risk(self) -> dict[str, Any]:
        return self.raw.get("risk", {})

    @property
    def schedule(self) -> dict[str, Any]:
        return self.raw.get("schedule", {})

    @property
    def events(self) -> dict[str, Any]:
        return self.raw.get("events", {})

    @property
    def mcp(self) -> dict[str, Any]:
        return self.raw.get("mcp", {})

    @property
    def runtime(self) -> dict[str, Any]:
        return self.raw.get("runtime", {})

    @property
    def backtest(self) -> dict[str, Any]:
        return self.raw.get("backtest", {})


def _default_config() -> dict[str, Any]:
    return {
        "runtime": {"mode": "live"},
        "backtest": {
            "clock_start": "2025-01-06T08:00:00Z",
            "clock_end": "2025-01-10T16:30:00Z",
            "daily_notional_min": 5000,
            "daily_notional_max": 10000,
            "simulated_wait_seconds": 2,
        },
        "models": {"strategy_director": "claude-4-6-opus-latest"},
        "anthropic": {"thinking": "adaptive", "xml_repair_max_retries": 2},
        "universe": {"holdings": ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","NFLX","AVGO"], "watchlist": ["JPM","BAC","XOM","CVX","UNH","LLY","PFE","JNJ","COST","WMT","HD","NKE","KO","PEP","DIS","INTC","QCOM","ADBE","CRM","ORCL"]},
        "risk": {"min_edge_after_cost_pct": 0.0, "min_win_prob": 0.0},
        "schedule": {"adaptive": {}},
        "events": {"earnings_window_days": {"start": -1, "end": 2}},
        "mcp": {"quotas": {}},
    }


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(path: str | Path = "config/default.yaml") -> AppConfig:
    defaults = _default_config()
    if importlib.util.find_spec("yaml") is None:
        return AppConfig(raw=defaults)

    import yaml

    with open(path, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}
    return AppConfig(raw=_deep_merge(defaults, loaded))
