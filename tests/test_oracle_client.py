import pytest
pytest.importorskip("aiosqlite")

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trading.config import AppConfig
from trading.data.oracle_client import OracleClient, OracleQuery
from trading.db.models import Base, HistoricalSnapshot
from trading.utils.time_provider import SimulatedClock, TimeProvider


@pytest.mark.asyncio
async def test_oracle_client_backtest_returns_historical_payload():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        session.add(
            HistoricalSnapshot(
                run_id="r1",
                provider="FINNHUB",
                provider_endpoint="finnhub_quote",
                symbol="AAPL",
                request_params_json={"symbol": "AAPL"},
                response_json='{"c":123.4}',
                event_timestamp=datetime(2025, 1, 6, 8, 0, tzinfo=timezone.utc),
                published_at=datetime(2025, 1, 6, 8, 0, tzinfo=timezone.utc),
                payload_hash="h",
                leakage_flag=False,
            )
        )
        await session.commit()

    tp = TimeProvider(mode="backtest", simulated_clock=SimulatedClock(datetime(2025, 1, 6, 9, 0, tzinfo=timezone.utc)))
    cfg = AppConfig(raw={"runtime": {"mode": "backtest"}})
    client = OracleClient(cfg, tp, session_factory)
    payload = await client.fetch(OracleQuery(provider_endpoint="finnhub_quote", symbol="AAPL", params={"symbol": "AAPL"}))
    assert payload == '{"c":123.4}'
