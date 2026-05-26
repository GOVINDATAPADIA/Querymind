"""Agent state definition for the QueryMind LangGraph workflow."""

from typing import TypedDict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Complete state carried through every node in the query-processing graph.

    Each field tracks one aspect of the user query lifecycle — from raw question
    through SQL generation, execution, interpretation, and response assembly.
    """

    # ── User input ───────────────────────────────────────────────────────
    user_question: str
    conversation_history: list[BaseMessage]

    # ── Schema & SQL ─────────────────────────────────────────────────────
    schema_context: str
    generated_sql: str
    sql_error: str | None

    # ── Query execution ──────────────────────────────────────────────────
    query_result: Any  # pandas DataFrame — typed as Any for TypedDict compat
    result_truncated: bool
    retry_count: int

    # ── Safety gate ──────────────────────────────────────────────────────
    is_safe: bool
    safety_reason: str

    # ── Response assembly ────────────────────────────────────────────────
    plain_english_answer: str
    chart_suggestion: dict | None
    follow_up_suggestions: list[str]
    final_response: dict | None

    # ── Metadata ─────────────────────────────────────────────────────────
    session_id: str
    execution_time_ms: float
