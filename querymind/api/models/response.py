"""Response models for the QueryMind API."""

from pydantic import BaseModel, Field
from typing import Any


class QueryResponse(BaseModel):
    """Response body for the POST /query endpoint."""

    sql_generated: str = Field(default="", description="The SQL query that was generated")
    result_table: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Query results as list of row dicts, max 100 rows",
    )
    plain_english: str = Field(
        default="", description="Plain English interpretation of results"
    )
    chart_suggestion: dict[str, Any] | None = Field(
        default=None, description="Plotly-compatible chart specification"
    )
    follow_up_suggestions: list[str] = Field(
        default_factory=list, description="Suggested follow-up questions"
    )
    retry_count: int = Field(
        default=0, description="Number of SQL correction retries used"
    )
    execution_time_ms: float = Field(
        default=0, description="Total pipeline execution time in milliseconds"
    )
    session_id: str = Field(
        default="", description="Session ID for conversational continuity"
    )


class SchemaTable(BaseModel):
    """Schema information for a single table."""

    name: str
    columns: list[dict[str, str]]
    primary_keys: list[str]
    foreign_keys: list[dict[str, str]]


class SchemaResponse(BaseModel):
    """Response body for the GET /schema endpoint."""

    tables: list[SchemaTable] = Field(default_factory=list)
    relationships: list[dict[str, str]] = Field(default_factory=list)
    total_columns: int = Field(default=0)


class HealthResponse(BaseModel):
    """Response body for the GET /health endpoint."""

    status: str = Field(default="ok")
    db_connected: bool = Field(default=False)
    llm_connected: bool = Field(default=False)


class ErrorResponse(BaseModel):
    """Structured error response — never exposes raw internals."""

    error: str
    error_code: str
    suggestion: str = Field(default="")
