"""Safe, async SQL query execution with timeout and result-size guards.

Executes user-facing SQL queries via the async SQLAlchemy engine, converts
results to pandas DataFrames, and enforces row-count limits.  Raw error
details are never exposed to callers.
"""

from __future__ import annotations

import asyncio
import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from config import get_settings
from db.connection import get_engine

logger = logging.getLogger(__name__)


async def execute_query(
    sql: str,
    engine: AsyncEngine | None = None,
) -> tuple[pd.DataFrame, str | None]:
    """Execute a SQL query and return the results as a DataFrame.

    Parameters
    ----------
    sql:
        The SQL string to execute (should already be validated by
        :mod:`core.safety_validator`).
    engine:
        Optional async engine override.  Falls back to the default engine
        from :func:`db.connection.get_engine`.

    Returns
    -------
    tuple[pd.DataFrame, str | None]
        A 2-tuple of ``(dataframe, error_message)``.
        On success ``error_message`` is ``None``; on failure the DataFrame is
        empty and ``error_message`` contains a sanitised description.
    """
    settings = get_settings()

    if engine is None:
        engine = get_engine()

    empty_df = pd.DataFrame()

    try:
        async def _run_query() -> tuple[pd.DataFrame, str | None]:
            async with engine.connect() as conn:
                result = await conn.execute(text(sql))
                columns = list(result.keys())
                rows = result.fetchall()

                df = pd.DataFrame(rows, columns=columns)

                warning: str | None = None
                if len(df) > settings.max_result_rows:
                    warning = (
                        f"Result truncated: showing {settings.max_result_rows} "
                        f"of {len(df)} rows."
                    )
                    df = df.head(settings.max_result_rows)

                return df, warning

        # Enforce a hard 5-second timeout on the entire query round-trip
        df, warning = await asyncio.wait_for(_run_query(), timeout=5.0)
        logger.info(
            "Query executed successfully — %d rows returned.", len(df),
        )
        return df, warning

    except asyncio.TimeoutError:
        logger.warning("Query timed out after 5 seconds.")
        return empty_df, "Query timed out. Please simplify your query or add filters."

    except SQLAlchemyError as exc:
        # Log the real error internally but sanitise the outward message
        logger.error("SQLAlchemy error during query execution: %s", exc, exc_info=True)
        return empty_df, "A database error occurred while executing your query."

    except Exception as exc:
        logger.error("Unexpected error during query execution: %s", exc, exc_info=True)
        return empty_df, "An unexpected error occurred. Please try again."
