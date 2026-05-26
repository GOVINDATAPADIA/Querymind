"""Async SQLAlchemy engine factory with singleton pattern and health checks."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from config import get_settings

logger = logging.getLogger(__name__)

# ── Module-level singleton ───────────────────────────────────────────────────
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _is_sqlite(url: str) -> bool:
    """Check if the database URL targets SQLite."""
    return "sqlite" in url.lower()


def get_engine() -> AsyncEngine:
    """Return the async engine, creating it on first call (singleton).

    Pool settings differ by dialect:
    - PostgreSQL (asyncpg): pool_size=5, max_overflow=10, pool_pre_ping=True
    - SQLite (aiosqlite): check_same_thread=False, static pool
    """
    global _engine, _session_factory

    if _engine is not None:
        return _engine

    settings = get_settings()
    url = settings.database_url
    logger.info("Creating async engine for dialect: %s", settings.db_dialect)

    if _is_sqlite(url):
        _engine = create_async_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
            # SQLite doesn't benefit from a connection pool — use NullPool-like
            # behaviour via StaticPool for single-file dev databases.
            pool_pre_ping=True,
        )
    else:
        # PostgreSQL (or any other full RDBMS)
        _engine = create_async_engine(
            url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("Async engine created successfully.")
    return _engine


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a ready-to-use session.

    Usage::

        async with get_async_session() as session:
            result = await session.execute(text("SELECT 1"))

    The session is committed on clean exit and rolled back on exception.
    """
    # Ensure the engine (and therefore the session factory) exists.
    get_engine()
    assert _session_factory is not None, "Session factory was not initialised."

    session: AsyncSession = _session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_db_health() -> bool:
    """Run a lightweight ``SELECT 1`` probe and return *True* if the database
    is reachable, *False* otherwise.
    """
    try:
        async with get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            row = result.scalar_one_or_none()
            healthy = row == 1
            if healthy:
                logger.debug("Database health check passed.")
            else:
                logger.warning("Database health check returned unexpected value: %s", row)
            return healthy
    except Exception as exc:
        logger.error("Database health check failed: %s", exc, exc_info=True)
        return False


async def dispose_engine() -> None:
    """Dispose the async engine and release all pooled connections.

    Safe to call even if the engine was never created.
    """
    global _engine, _session_factory

    if _engine is not None:
        logger.info("Disposing async engine …")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Engine disposed.")
