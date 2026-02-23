from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Awaitable, Callable

from trading.config import AppConfig
from trading.core.trade_gate import TradeGate
from trading.utils.time_provider import SimulatedClock, TimeProvider

RunHook = Callable[[str, datetime], Awaitable[None]]


@dataclass
class BacktestRunner:
    config: AppConfig
    run_hook: RunHook

    def __post_init__(self) -> None:
        bt = self.config.backtest
        start = _parse_iso(bt.get("clock_start", "2025-01-06T08:00:00Z"))
        self.clock = SimulatedClock(current=start)
        self.time_provider = TimeProvider(mode="backtest", simulated_clock=self.clock)
        self.trade_gate = TradeGate(config=self.config)

    async def run(self) -> None:
        bt = self.config.backtest
        end = _parse_iso(bt.get("clock_end", "2025-01-10T16:30:00Z"))
        wait_seconds = int(bt.get("simulated_wait_seconds", 2))

        current_day = self.clock.now().date()
        while current_day <= end.date():
            for name, event_time in self._daily_windows(current_day):
                if event_time < self.clock.now() or event_time > end:
                    continue
                self.clock.advance_to(event_time)
                await self.run_hook(name, self.time_provider.now())
                await asyncio.sleep(wait_seconds)
            current_day = current_day + timedelta(days=1)

    def _daily_windows(self, day: date) -> list[tuple[str, datetime]]:
        windows = self.config.schedule.get("windows", {})
        premarket = _combine(day, windows.get("premarket", "08:00"))
        open_plus = _combine(day, "09:30") + timedelta(minutes=int(windows.get("open_plus_minutes", 20)))
        noon = _combine(day, windows.get("noon", "12:00"))
        reflection = _combine(day, windows.get("reflection", "16:30"))
        return [
            ("premarket", premarket),
            ("open_plus", open_plus),
            ("noon", noon),
            ("reflection", reflection),
        ]

    def allow_order_notional(self, existing_daily_notional: float, proposed_notional: float) -> bool:
        return self.trade_gate.enforce_backtest_notional_cap(
            existing_daily_notional=existing_daily_notional,
            proposed_notional=proposed_notional,
        )


def _parse_iso(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _combine(day: date, hm: str) -> datetime:
    hour, minute = hm.split(":", 1)
    return datetime(day.year, day.month, day.day, int(hour), int(minute), tzinfo=timezone.utc)
