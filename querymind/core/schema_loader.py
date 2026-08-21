"""Dynamic SQLAlchemy schema introspection with TTL-based caching.

Introspects the connected database to build a schema dictionary containing
tables, columns, types, primary keys, and foreign keys.  The schema is
formatted into a compact string suitable for injection into LLM prompts,
and can be filtered to only the tables relevant to a given user question.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncEngine

from config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level TTL cache
# ---------------------------------------------------------------------------
_schema_cache: dict[str, Any] = {
    "schema": {},
    "timestamp": 0.0,
}


# ---------------------------------------------------------------------------
# Core introspection
# ---------------------------------------------------------------------------

async def load_schema(engine: AsyncEngine) -> dict[str, Any]:
    """Introspect the database and return the full schema dictionary.

    Returns a dict of the form::

        {
            "table_name": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
                    ...
                ],
                "primary_keys": ["id"],
                "foreign_keys": [
                    {"column": "user_id", "referred_table": "users", "referred_column": "id"},
                    ...
                ],
            },
            ...
        }
    """
    try:
        def _inspect_sync(connection) -> dict[str, Any]:
            """Synchronous introspection callback executed via run_sync."""
            inspector = sa_inspect(connection)
            schema: dict[str, Any] = {}

            for table_name in inspector.get_table_names():
                columns_raw = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                fk_list = inspector.get_foreign_keys(table_name)

                pk_names: list[str] = pk_constraint.get("constrained_columns", [])

                columns: list[dict[str, Any]] = []
                for col in columns_raw:
                    columns.append({
                        "name": col["name"],
                        "type": str(col["type"]),
                        "primary_key": col["name"] in pk_names,
                        "nullable": col.get("nullable", True),
                    })

                foreign_keys: list[dict[str, str]] = []
                for fk in fk_list:
                    referred_table = fk.get("referred_table", "")
                    constrained = fk.get("constrained_columns", [])
                    referred = fk.get("referred_columns", [])
                    for c_col, r_col in zip(constrained, referred):
                        foreign_keys.append({
                            "column": c_col,
                            "referred_table": referred_table,
                            "referred_column": r_col,
                        })

                schema[table_name] = {
                    "columns": columns,
                    "primary_keys": pk_names,
                    "foreign_keys": foreign_keys,
                }

            return schema

        async with engine.connect() as conn:
            schema = await conn.run_sync(_inspect_sync)

        logger.info("Schema introspection complete — %d tables found.", len(schema))
        return schema

    except Exception:
        logger.warning("Schema introspection failed.", exc_info=True)
        return {}


# ---------------------------------------------------------------------------
# Formatting for LLM prompt injection
# ---------------------------------------------------------------------------

def format_schema_context(schema: dict[str, Any]) -> str:
    """Format the schema dictionary into a clean string for prompt injection."""
    if not schema:
        return "No schema available."

    if "tables" in schema and isinstance(schema["tables"], dict):
        schema = schema["tables"]

    parts: list[str] = []
    for table_name, table_info in schema.items():
        if not isinstance(table_info, dict) or "columns" not in table_info:
            continue
        col_strs: list[str] = []
        for col in table_info["columns"]:
            label = col["name"]
            col_type = col.get("type", "TEXT")
            suffix_parts: list[str] = [str(col_type)]
            if col.get("primary_key"):
                suffix_parts.append("PK")
            col_strs.append(f"{label} ({', '.join(suffix_parts)})")

        fk_entries = table_info.get("foreign_keys", [])
        if fk_entries:
            fk_strs = [
                f"{fk['column']} -> {fk['referred_table']}.{fk['referred_column']}"
                for fk in fk_entries
            ]
            fk_line = ", ".join(fk_strs)
        else:
            fk_line = "none"

        parts.append(
            f"Table: {table_name}\n"
            f"Columns: {', '.join(col_strs)}\n"
            f"Foreign Keys: {fk_line}"
        )

    return "\n\n".join(parts) if parts else "No schema available."


# ---------------------------------------------------------------------------
# Relevance filtering
# ---------------------------------------------------------------------------

async def get_relevant_tables(
    schema: dict[str, Any],
    question: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Return a subset of the schema containing only tables relevant to *question*."""
    if not schema:
        return {}

    was_wrapped = "tables" in schema and isinstance(schema["tables"], dict)
    tables_dict = schema["tables"] if was_wrapped else schema

    # Normalise question tokens for case-insensitive matching
    question_lower = question.lower()
    tokens = set(question_lower.split())

    scored: list[tuple[str, int, dict[str, Any]]] = []

    for table_name, table_info in tables_dict.items():
        if not isinstance(table_info, dict):
            continue
        score = 0
        table_lower = table_name.lower()

        # Direct table-name mention in question
        if table_lower in question_lower:
            score += 10

        # Singular/plural fuzzy match (simple heuristic)
        if table_lower.rstrip("s") in question_lower or table_lower + "s" in question_lower:
            score += 5

        # Token overlap with table name parts (split on underscores)
        table_parts = set(table_lower.split("_"))
        overlap = tokens & table_parts
        score += len(overlap) * 3

        # Column name mentions
        for col in table_info.get("columns", []):
            col_lower = col["name"].lower()
            if col_lower in question_lower:
                score += 4
            col_parts = set(col_lower.split("_"))
            if tokens & col_parts:
                score += 2

        # Foreign-key reference mentions
        for fk in table_info.get("foreign_keys", []):
            ref_lower = fk.get("referred_table", "").lower()
            if ref_lower in question_lower:
                score += 3

        scored.append((table_name, score, table_info))

    # Sort descending by score; if all scores are 0, return all tables (capped at top_k)
    scored.sort(key=lambda item: item[1], reverse=True)

    selected: dict[str, Any] = {}
    for table_name, _, table_info in scored[:top_k]:
        selected[table_name] = table_info

    # Secondary pass: pull in tables referenced by foreign keys of selected tables
    fk_additions: dict[str, Any] = {}
    for table_info in selected.values():
        for fk in table_info.get("foreign_keys", []):
            ref_table = fk.get("referred_table", "")
            if ref_table in tables_dict and ref_table not in selected:
                fk_additions[ref_table] = tables_dict[ref_table]

    selected.update(fk_additions)
    return {"tables": selected} if was_wrapped else selected


# ---------------------------------------------------------------------------
# TTL-cached access
# ---------------------------------------------------------------------------

async def get_cached_schema(engine: AsyncEngine) -> dict[str, Any]:
    """Return the cached schema if still valid, otherwise re-introspect.

    The TTL is controlled by ``settings.schema_cache_ttl`` (seconds).
    """
    settings = get_settings()
    now = time.time()

    if (
        _schema_cache["schema"]
        and (now - _schema_cache["timestamp"]) < settings.schema_cache_ttl
    ):
        logger.debug("Returning cached schema (age=%.1fs).", now - _schema_cache["timestamp"])
        return _schema_cache["schema"]

    logger.info("Schema cache miss or expired — re-introspecting.")
    schema = await load_schema(engine)
    _schema_cache["schema"] = schema
    _schema_cache["timestamp"] = now
    return schema
