from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from trading.config import AppConfig
from trading.db.models import HistoricalSnapshot
from trading.utils.time_provider import TimeProvider


@dataclass
class OracleQuery:
    provider_endpoint: str
    symbol: str | None
    params: dict[str, Any]


class OracleClient:
    """Proxy layer that serves live MarketOracle responses or PIT snapshots in backtest mode."""

    def __init__(
        self,
        config: AppConfig,
        time_provider: TimeProvider,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.config = config
        self.time_provider = time_provider
        self.session_factory = session_factory

    async def fetch(self, query: OracleQuery) -> str:
        mode = self.config.runtime.get("mode", "live")
        if mode == "backtest":
            return await self._fetch_backtest(query)
        return self._fetch_live(query)

    def _fetch_live(self, query: OracleQuery) -> str:
        from trading.data import mcp_server

        tool_name = query.provider_endpoint
        tool = getattr(mcp_server, tool_name, None)
        if tool is None:
            return json.dumps({"error": f"unknown_tool:{tool_name}"})
        try:
            return str(tool(**query.params))
        except TypeError:
            return str(tool())

    async def _fetch_backtest(self, query: OracleQuery) -> str:
        now = self.time_provider.now()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        statement: Select[tuple[HistoricalSnapshot]] = (
            select(HistoricalSnapshot)
            .where(HistoricalSnapshot.provider_endpoint == query.provider_endpoint)
            .where(HistoricalSnapshot.published_at <= now)
            .order_by(desc(HistoricalSnapshot.published_at))
            .limit(1)
        )
        if query.symbol is not None:
            statement = statement.where(HistoricalSnapshot.symbol == query.symbol)

        async with self.session_factory() as session:
            row = (await session.execute(statement)).scalars().first()

        if row is None:
            return json.dumps(
                {
                    "error": "DATA_MISSING_AT_TIME",
                    "provider_endpoint": query.provider_endpoint,
                    "symbol": query.symbol,
                    "as_of": now.isoformat(),
                }
            )
        return row.response_json
