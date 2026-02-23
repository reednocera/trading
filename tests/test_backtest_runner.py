import asyncio
from datetime import datetime

from trading.backtest.runner import BacktestRunner
from trading.config import AppConfig


def test_backtest_runner_windows_and_notional_cap():
    seen = []

    async def hook(name: str, ts: datetime) -> None:
        seen.append((name, ts))

    cfg = AppConfig(
        raw={
            "runtime": {"mode": "backtest"},
            "backtest": {
                "clock_start": "2025-01-06T08:00:00Z",
                "clock_end": "2025-01-06T16:30:00Z",
                "daily_notional_min": 5000,
                "daily_notional_max": 10000,
                "simulated_wait_seconds": 0,
            },
            "schedule": {
                "windows": {
                    "premarket": "08:00",
                    "open_plus_minutes": 20,
                    "noon": "12:00",
                    "reflection": "16:30",
                }
            },
        }
    )

    runner = BacktestRunner(config=cfg, run_hook=hook)
    asyncio.run(runner.run())

    names = [n for n, _ in seen]
    assert names == ["premarket", "open_plus", "noon", "reflection"]
    assert runner.allow_order_notional(2000, 3500)
    assert not runner.allow_order_notional(9500, 600)
