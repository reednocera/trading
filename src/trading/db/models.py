from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class RegimeHistory(Base):
    __tablename__ = "regime_history"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    as_of: Mapped[datetime] = mapped_column(DateTime, index=True)
    regime_json: Mapped[dict] = mapped_column(JSON)


class QuotaUsage(Base):
    __tablename__ = "quota_usage"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    provider: Mapped[str] = mapped_column(String, index=True)
    window_type: Mapped[str] = mapped_column(String)
    used_count: Mapped[float] = mapped_column(Float)
    remaining_count: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class EvidenceStore(Base):
    __tablename__ = "evidence_store"

    evidence_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_uri: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String, index=True)
    payload_path: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON)


class AttributionMetric(Base):
    __tablename__ = "attribution_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    strategy: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[str] = mapped_column(String, index=True)
    expected_value_after_cost: Mapped[float] = mapped_column(Float)
    realized_pnl: Mapped[float] = mapped_column(Float)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, index=True)
    bid: Mapped[float] = mapped_column(Float)
    ask: Mapped[float] = mapped_column(Float)
    mid: Mapped[float] = mapped_column(Float)
    spread: Mapped[float] = mapped_column(Float)
    last: Mapped[float] = mapped_column(Float)


class HistoricalSnapshot(Base):
    __tablename__ = "historical_snapshot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    provider_endpoint: Mapped[str] = mapped_column(String(128), index=True)
    symbol: Mapped[str | None] = mapped_column(String(16), index=True, nullable=True)
    request_params_json: Mapped[dict] = mapped_column(JSON)
    response_json: Mapped[str] = mapped_column(Text)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    payload_hash: Mapped[str] = mapped_column(String(128), index=True)
    leakage_flag: Mapped[bool] = mapped_column(Boolean, default=False)


class BacktestPortfolioState(Base):
    __tablename__ = "backtest_portfolio_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id: Mapped[str] = mapped_column(String(64), index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    equity: Mapped[float] = mapped_column(Float)
    cash: Mapped[float] = mapped_column(Float)
    margin_used: Mapped[float] = mapped_column(Float)
    gross_exposure: Mapped[float] = mapped_column(Float)
    net_exposure: Mapped[float] = mapped_column(Float)


class BacktestPosition(Base):
    __tablename__ = "backtest_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id: Mapped[str] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    avg_cost: Mapped[float] = mapped_column(Float, default=0.0)
    mark_price: Mapped[float] = mapped_column(Float, default=0.0)
    unrealized_pnl: Mapped[float] = mapped_column(Float, default=0.0)


class BacktestOrder(Base):
    __tablename__ = "backtest_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id: Mapped[str] = mapped_column(String(64), index=True)
    decision_run_id: Mapped[str] = mapped_column(String(64), index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    side: Mapped[str] = mapped_column(String(16))
    qty: Mapped[float] = mapped_column(Float)
    notional: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)


class BacktestFill(Base):
    __tablename__ = "backtest_fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    backtest_run_id: Mapped[str] = mapped_column(String(64), index=True)
    order_id: Mapped[int] = mapped_column(Integer, index=True)
    filled_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    fill_price: Mapped[float] = mapped_column(Float)
    qty: Mapped[float] = mapped_column(Float)
    fees: Mapped[float] = mapped_column(Float, default=0.0)
