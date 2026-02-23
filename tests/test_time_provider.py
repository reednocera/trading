from datetime import datetime, timezone

from trading.utils.time_provider import SimulatedClock, TimeProvider


def test_time_provider_live_returns_utc_datetime():
    tp = TimeProvider(mode="live")
    now = tp.now()
    assert now.tzinfo is not None


def test_time_provider_backtest_uses_simulated_clock():
    start = datetime(2025, 1, 6, 8, 0, tzinfo=timezone.utc)
    clock = SimulatedClock(start)
    tp = TimeProvider(mode="backtest", simulated_clock=clock)
    assert tp.now() == start
    clock.advance_seconds(120)
    assert tp.now().minute == 2
