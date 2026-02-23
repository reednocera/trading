from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from trading.data.oracle_client import OracleClient, OracleQuery
from trading.db.models import HistoricalSnapshot


@dataclass
class HarvestRecord:
    provider: str
    provider_endpoint: str
    symbol: str | None
    request_params: dict[str, Any]
    response_json: str
    event_timestamp: datetime
    published_at: datetime


class HistoricalHarvester:
    def __init__(
        self,
        oracle_client: OracleClient,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.oracle_client = oracle_client
        self.session_factory = session_factory

    async def harvest_symbol_prices(self, symbols: list[str], run_id: str | None = None) -> str:
        run_id = run_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        records: list[HarvestRecord] = []
        for symbol in symbols:
            payload = await self.oracle_client.fetch(
                OracleQuery(provider_endpoint="get_price", symbol=symbol, params={"symbol": symbol})
            )
            records.append(
                HarvestRecord(
                    provider="MARKET_ORACLE",
                    provider_endpoint="get_price",
                    symbol=symbol,
                    request_params={"symbol": symbol},
                    response_json=payload,
                    event_timestamp=now,
                    published_at=now,
                )
            )
        await self.persist_records(run_id=run_id, records=records)
        return run_id

    @staticmethod
    def parse_published_at(payload: str, fallback: datetime) -> datetime:
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            return fallback

        for key in ("published_at", "datetime", "timestamp"):
            value = decoded.get(key)
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    continue
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(float(value), tz=timezone.utc)
        return fallback

    @staticmethod
    def is_forward_looking_summary(payload: str) -> bool:
        lowered = payload.lower()
        markers = ["weekly recap", "month in review", "year ahead", "next week"]
        return any(marker in lowered for marker in markers)

    async def persist_records(self, run_id: str, records: list[HarvestRecord]) -> int:
        inserted = 0
        async with self.session_factory() as session:
            for rec in records:
                if self.is_forward_looking_summary(rec.response_json):
                    continue
                published_at = self.parse_published_at(rec.response_json, rec.published_at)
                payload_hash = hashlib.sha256(rec.response_json.encode("utf-8")).hexdigest()
                session.add(
                    HistoricalSnapshot(
                        run_id=run_id,
                        provider=rec.provider,
                        provider_endpoint=rec.provider_endpoint,
                        symbol=rec.symbol,
                        request_params_json=rec.request_params,
                        response_json=rec.response_json,
                        event_timestamp=rec.event_timestamp,
                        published_at=published_at,
                        payload_hash=payload_hash,
                    )
                )
                inserted += 1
            await session.commit()
        return inserted
