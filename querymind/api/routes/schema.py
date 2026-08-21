"""Schema introspection endpoint."""

import logging
from fastapi import APIRouter, HTTPException
from api.models.response import SchemaResponse, SchemaTable, ErrorResponse
from db.connection import get_engine
from core.schema_loader import get_cached_schema

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/schema",
    response_model=SchemaResponse,
    responses={503: {"model": ErrorResponse}},
    tags=["Schema"],
)
async def get_schema() -> SchemaResponse:
    """Return the introspected database schema with tables, columns, and relationships."""
    try:
        engine = get_engine()
        schema = await get_cached_schema(engine)
    except Exception as e:
        logger.error(f"Schema introspection failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to introspect database schema",
                "error_code": "SCHEMA_ERROR",
                "suggestion": "Check database connectivity and try again",
            },
        )

    tables: list[SchemaTable] = []
    relationships: list[dict[str, str]] = []
    total_columns = 0

    tables_dict = schema.get("tables", {}) if (isinstance(schema, dict) and "tables" in schema) else (schema if isinstance(schema, dict) else {})

    for table_name, table_info in tables_dict.items():
        if not isinstance(table_info, dict):
            continue
        columns = [
            {"name": col["name"], "type": str(col.get("type", "TEXT"))}
            for col in table_info.get("columns", [])
        ]
        total_columns += len(columns)

        pks = table_info.get("primary_keys", [])

        fks: list[dict[str, str]] = []
        for fk in table_info.get("foreign_keys", []):
            fk_info = {
                "column": fk.get("column", ""),
                "references_table": fk.get("referred_table", ""),
                "references_column": fk.get("referred_column", ""),
            }
            fks.append(fk_info)
            relationships.append(
                {
                    "from_table": table_name,
                    "from_column": fk.get("column", ""),
                    "to_table": fk.get("referred_table", ""),
                    "to_column": fk.get("referred_column", ""),
                }
            )

        tables.append(
            SchemaTable(
                name=table_name,
                columns=columns,
                primary_keys=pks,
                foreign_keys=fks,
            )
        )

    return SchemaResponse(
        tables=tables,
        relationships=relationships,
        total_columns=total_columns,
    )
