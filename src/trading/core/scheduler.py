from __future__ import annotations

from dataclasses import dataclass

from trading.config import AppConfig


@dataclass
class AdaptiveInputs:
    event_velocity: float
    volatility_state: str
    quota_pressure: float


@dataclass
class AdaptiveIntervalScheduler:
    config: AppConfig

    def next_interval_minutes(self, inputs: AdaptiveInputs) -> int:
        adaptive = self.config.schedule.get("adaptive", {})
        quiet_interval = int(adaptive.get("quiet_interval_minutes", 90))
        active_interval = int(adaptive.get("active_interval_minutes", 30))
        max_interval = int(adaptive.get("max_interval_minutes", 120))
        high_velocity = float(adaptive.get("high_event_velocity_threshold", 0.7))
        high_quota = float(adaptive.get("high_quota_pressure_threshold", 0.85))

        if inputs.quota_pressure > high_quota:
            return max_interval
        if inputs.event_velocity > high_velocity or inputs.volatility_state == "high":
            return active_interval
        return quiet_interval

    def windows(self) -> dict[str, str | int]:
        return self.config.schedule.get("windows", {})
