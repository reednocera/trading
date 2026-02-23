from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def build_session_factory() -> async_sessionmaker[AsyncSession]:
    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/trading")
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)
