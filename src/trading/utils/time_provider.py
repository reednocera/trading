from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class SimulatedClock:
    current: datetime

    def now(self) -> datetime:
        return self.current

    def advance_to(self, next_dt: datetime) -> datetime:
        if next_dt.tzinfo is None:
            next_dt = next_dt.replace(tzinfo=timezone.utc)
        self.current = next_dt
        return self.current

    def advance_seconds(self, seconds: int) -> datetime:
        self.current = self.current + timedelta(seconds=seconds)
        return self.current


class TimeProvider:
    def __init__(self, mode: str = "live", simulated_clock: SimulatedClock | None = None) -> None:
        self.mode = mode
        self.simulated_clock = simulated_clock

    def now(self) -> datetime:
        if self.mode == "backtest":
            if self.simulated_clock is None:
                raise ValueError("backtest mode requires a SimulatedClock")
            return self.simulated_clock.now()
        return datetime.now(timezone.utc)

    def set_mode(self, mode: str, simulated_clock: SimulatedClock | None = None) -> None:
        self.mode = mode
        self.simulated_clock = simulated_clock
