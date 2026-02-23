from __future__ import annotations

from pydantic import BaseModel, Field


class ThesisMetrics(BaseModel):
    expected_return_pct: float
    expected_value_pct: float
    win_prob: float
    avg_win_pct: float
    avg_loss_pct: float
    max_loss_pct: float
    time_stop_days: int
    price_invalidator: float
    cost_estimate_pct: float
    edge_after_cost_pct: float


class TradeOrder(BaseModel):
    symbol: str
    side: str
    qty: float
    risk_units: float
    bid_at_submit: float | None = None
    ask_at_submit: float | None = None
    mid_at_submit: float | None = None
    slippage_model_id: str | None = None
    estimated_slippage: float | None = None
    fill_rule: str | None = None


class TradePlanV11(BaseModel):
    schema_version: str = Field(default="1.1")
    decision: str
    expected_value_after_cost: float
    orders: list[TradeOrder]
    reasons_to_hold: list[str] = []
    reasons_to_exit: list[str] = []
    alternatives_considered: list[dict] = []
