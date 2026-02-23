from trading.config import AppConfig
from trading.core.scheduler import AdaptiveInputs, AdaptiveIntervalScheduler


def test_scheduler_high_activity_uses_active_interval():
    cfg = AppConfig(raw={"schedule": {"adaptive": {"active_interval_minutes": 45, "high_event_velocity_threshold": 0.7, "high_quota_pressure_threshold": 0.85}}})
    s = AdaptiveIntervalScheduler(config=cfg)
    i = s.next_interval_minutes(AdaptiveInputs(event_velocity=0.9, volatility_state="high", quota_pressure=0.1))
    assert i == 45
