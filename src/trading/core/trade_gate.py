from __future__ import annotations

from dataclasses import dataclass

from trading.config import AppConfig


@dataclass
class TradeGate:
    config: AppConfig

    def passes_thresholds(self, *, edge_after_cost_pct: float, win_prob: float) -> bool:
        return (
            edge_after_cost_pct >= float(self.config.risk.get("min_edge_after_cost_pct", 0.0))
            and win_prob >= float(self.config.risk.get("min_win_prob", 0.0))
        )

    def enforce_backtest_notional_cap(self, *, existing_daily_notional: float, proposed_notional: float) -> bool:
        if self.config.runtime.get("mode", "live") != "backtest":
            return True
        minimum = float(self.config.backtest.get("daily_notional_min", 5000))
        maximum = float(self.config.backtest.get("daily_notional_max", 10000))
        projected = existing_daily_notional + proposed_notional
        return minimum <= projected <= maximum
