"""LangGraph node functions for the QueryMind agentic pipeline.

Each node is an async function that receives the full ``AgentState`` dict
and returns a **partial** state update dict.  Nodes are wired together by
the graph defined in :mod:`agent.graph`.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

import pandas as pd

from config import get_settings
from agent.state import AgentState
from agent.prompts import (
    SQL_GENERATION_PROMPT,
    SQL_FIX_PROMPT,
    RESULT_INTERPRETATION_PROMPT,
    FOLLOWUP_PROMPT,
)
from core.schema_loader import get_cached_schema, format_schema_context, get_relevant_tables
from core.sql_executor import execute_query
from core.safety_validator import validate_sql, sanitize_sql_output
from core.memory_manager import memory_manager
from services.llm_provider import get_llm
from services.chart_suggester import suggest_chart
from db.connection import get_engine

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Schema Loading
# ─────────────────────────────────────────────────────────────────────────────

async def load_schema_node(state: AgentState) -> dict:
    """Introspect the database schema and filter to tables relevant to the question."""
    try:
        engine = get_engine()
        full_schema = await get_cached_schema(engine)

        if not full_schema:
            logger.warning("Schema introspection returned empty schema.")
            return {
                "schema_context": (
                    "Warning: Could not load database schema. "
                    "The SQL generation may be less accurate."
                ),
            }

        relevant_schema = await get_relevant_tables(full_schema, state["user_question"])
        formatted_context = format_schema_context(relevant_schema)

        logger.info(
            "Schema loaded — %d relevant tables selected from %d total.",
            len(relevant_schema),
            len(full_schema),
        )
        return {"schema_context": formatted_context}

    except Exception as exc:
        logger.error("Schema loading failed: %s", exc, exc_info=True)
        return {
            "schema_context": (
                "Warning: Failed to load database schema due to a connection error. "
                "SQL generation will proceed with limited context."
            ),
        }


# ─────────────────────────────────────────────────────────────────────────────
# 2. SQL Generation
# ─────────────────────────────────────────────────────────────────────────────

async def generate_sql_node(state: AgentState) -> dict:
    """Generate a SQL query from the user question using the LLM."""
    settings = get_settings()
    llm = get_llm()
    chain = SQL_GENERATION_PROMPT | llm

    # Build conversation history string for prompt injection
    history_parts: list[str] = []
    for msg in state.get("conversation_history", []):
        role = "User" if msg.type == "human" else "Assistant"
        history_parts.append(f"{role}: {msg.content}")
    history_str = "\n".join(history_parts) if history_parts else "No prior conversation."

    invoke_params = {
        "dialect": settings.db_dialect,
        "schema_context": state.get("schema_context", ""),
        "history": history_str,
        "question": state["user_question"],
    }

    # Retry with exponential backoff for transient LLM errors
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            response = await asyncio.wait_for(chain.ainvoke(invoke_params), timeout=30)
            sanitized_sql = sanitize_sql_output(response.content)
            logger.info("SQL generated successfully on attempt %d: %s", attempt, sanitized_sql[:120])
            return {"generated_sql": sanitized_sql}

        except Exception as exc:
            if attempt < max_attempts:
                backoff = 2 ** (attempt - 1)  # 1s, 2s
                logger.warning(
                    "LLM call failed (attempt %d/%d), retrying in %ds: %s",
                    attempt,
                    max_attempts,
                    backoff,
                    exc,
                )
                await asyncio.sleep(backoff)
            else:
                logger.error("LLM call failed after %d attempts: %s", max_attempts, exc)
                return {
                    "generated_sql": "",
                    "sql_error": f"Failed to generate SQL after {max_attempts} attempts: {exc}",
                }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Safety Validation
# ─────────────────────────────────────────────────────────────────────────────

async def validate_safety_node(state: AgentState) -> dict:
    """Run the generated SQL through the safety validator."""
    sql = state.get("generated_sql", "")

    if not sql:
        logger.warning("No SQL to validate — marking as unsafe.")
        return {"is_safe": False, "safety_reason": "No SQL query was generated."}

    result = validate_sql(sql)
    if not result.is_safe:
        logger.warning("SQL blocked by safety validator: %s", result.reason)
    else:
        logger.info("SQL passed safety validation.")

    return {"is_safe": result.is_safe, "safety_reason": result.reason}


# ─────────────────────────────────────────────────────────────────────────────
# 4. SQL Execution
# ─────────────────────────────────────────────────────────────────────────────

async def execute_sql_node(state: AgentState) -> dict:
    """Execute the generated SQL against the database."""
    settings = get_settings()
    engine = get_engine()

    try:
        df, error_msg = await execute_query(state["generated_sql"], engine)

        if error_msg and df.empty:
            # Execution failed entirely
            logger.warning("SQL execution error: %s", error_msg)
            return {"sql_error": error_msg, "query_result": None}

        # Determine if results were truncated
        truncated = error_msg is not None  # execute_query returns a warning string when truncated

        if truncated:
            logger.info("Query results truncated: %s", error_msg)

        logger.info("SQL executed successfully — %d rows returned.", len(df))
        return {
            "query_result": df,
            "sql_error": None,
            "result_truncated": truncated,
        }

    except Exception as exc:
        logger.error("Unexpected SQL execution failure: %s", exc, exc_info=True)
        return {"sql_error": str(exc), "query_result": None}





# ─────────────────────────────────────────────────────────────────────────────
# 6. SQL Fix (Self-Correction)
# ─────────────────────────────────────────────────────────────────────────────

async def fix_sql_node(state: AgentState) -> dict:
    """Ask the LLM to fix the failed SQL query based on the error message."""
    llm = get_llm()
    chain = SQL_FIX_PROMPT | llm

    current_retry = state.get("retry_count", 0)
    logger.info(
        "Attempting SQL fix (retry %d): error was '%s'",
        current_retry + 1,
        state.get("sql_error", "unknown"),
    )

    try:
        response = await asyncio.wait_for(
            chain.ainvoke({
                "schema_context": state.get("schema_context", ""),
                "sql": state.get("generated_sql", ""),
                "error": state.get("sql_error", "Unknown error"),
                "question": state["user_question"],
            }),
            timeout=30,
        )
        fixed_sql = sanitize_sql_output(response.content)
        logger.info("Fixed SQL generated: %s", fixed_sql[:120])

        return {
            "generated_sql": fixed_sql,
            "retry_count": current_retry + 1,
            "sql_error": None,
        }

    except Exception as exc:
        logger.error("LLM SQL-fix call failed: %s", exc, exc_info=True)
        return {
            "retry_count": current_retry + 1,
            "sql_error": f"Failed to auto-fix SQL: {exc}",
        }


# ─────────────────────────────────────────────────────────────────────────────
# 7. Result Interpretation
# ─────────────────────────────────────────────────────────────────────────────

def _build_result_summary(df: pd.DataFrame | None) -> str:
    """Create a compact text summary of a DataFrame for LLM consumption."""
    if df is None or df.empty:
        return "No results returned."

    rows, cols = df.shape

    if rows == 1:
        # Single-row result: show as key-value pairs
        pairs = [f"  {col}: {df.iloc[0][col]}" for col in df.columns]
        return f"Single row returned:\n" + "\n".join(pairs)

    # Multi-row result: shape + sample + numeric stats
    parts: list[str] = [f"Result shape: {rows} rows × {cols} columns"]

    # First 5 rows as a table
    sample = df.head(5).to_string(index=False)
    parts.append(f"First rows:\n{sample}")

    # Numeric column statistics
    numeric_df = df.select_dtypes(include=["number"])
    if not numeric_df.empty:
        stats = numeric_df.describe().to_string()
        parts.append(f"Numeric statistics:\n{stats}")

    return "\n\n".join(parts)


async def interpret_result_node(state: AgentState) -> dict:
    """Translate the SQL query results into a plain-English answer."""
    import re  # Ensure re is imported for regex stripping
    
    df = state.get("query_result")
    result_summary = _build_result_summary(df)

    try:
        llm = get_llm()
        chain = RESULT_INTERPRETATION_PROMPT | llm
        response = await asyncio.wait_for(
            chain.ainvoke({
                "question": state["user_question"],
                "sql": state.get("generated_sql", ""),
                "result_summary": result_summary,
            }),
            timeout=30,
        )
        
        # Strip internal <think>...</think> reasoning tags from models like Qwen/DeepSeek
        clean_answer = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
        
        logger.info("Result interpretation completed.")
        return {"plain_english_answer": clean_answer}

    except Exception as exc:
        logger.error("Result interpretation LLM call failed: %s", exc, exc_info=True)
        # Fallback: return the raw summary as the answer
        fallback = (
            f"Here are the results for your query. {result_summary}"
            if result_summary != "No results returned."
            else "Your query returned no results. Try broadening your search criteria."
        )
        return {"plain_english_answer": fallback}


# ─────────────────────────────────────────────────────────────────────────────
# 8. Chart Suggestion
# ─────────────────────────────────────────────────────────────────────────────

async def suggest_chart_node(state: AgentState) -> dict:
    """Suggest a chart type and specification based on the query results."""
    df = state.get("query_result")
    question = state.get("user_question", "")

    try:
        chart_spec = suggest_chart(df, question)
        if chart_spec:
            logger.info("Chart suggestion: %s", chart_spec.get("type", "none"))
        else:
            logger.info("No chart suggestion applicable for this result set.")
        return {"chart_suggestion": chart_spec}

    except Exception as exc:
        logger.warning("Chart suggestion failed: %s", exc)
        return {"chart_suggestion": None}


# ─────────────────────────────────────────────────────────────────────────────
# 9. Follow-Up Suggestions
# ─────────────────────────────────────────────────────────────────────────────

_GENERIC_FOLLOWUPS: list[str] = [
    "Can you break this down further by category?",
    "How does this compare to the previous period?",
    "What are the top 5 entries by this metric?",
]


async def suggest_followups_node(state: AgentState) -> dict:
    """Suggest 3 follow-up questions the user might ask next."""
    df = state.get("query_result")

    # Build context about the result shape
    if df is not None and not df.empty:
        result_rows = len(df)
        result_cols = len(df.columns)
        columns = ", ".join(df.columns.tolist())
    else:
        result_rows = 0
        result_cols = 0
        columns = "none"

    try:
        llm = get_llm()
        chain = FOLLOWUP_PROMPT | llm
        response = await asyncio.wait_for(
            chain.ainvoke({
                "question": state["user_question"],
                "result_rows": str(result_rows),
                "result_cols": str(result_cols),
                "columns": columns,
            }),
            timeout=30,
        )

        # Parse the JSON array from the LLM response
        content = response.content.strip()
        # Handle case where LLM wraps JSON in markdown code fences
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]  # Remove opening fence
            content = content.rsplit("```", 1)[0]  # Remove closing fence
            content = content.strip()

        suggestions = json.loads(content)

        if isinstance(suggestions, list) and len(suggestions) >= 3:
            suggestions = [str(s) for s in suggestions[:3]]
            logger.info("Follow-up suggestions generated successfully.")
            return {"follow_up_suggestions": suggestions}

        # If parsing succeeded but shape is unexpected, fall back
        logger.warning("LLM returned unexpected follow-up format: %s", suggestions)
        return {"follow_up_suggestions": _GENERIC_FOLLOWUPS}

    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Failed to parse follow-up suggestions JSON: %s", exc)
        return {"follow_up_suggestions": _GENERIC_FOLLOWUPS}

    except Exception as exc:
        logger.error("Follow-up suggestion LLM call failed: %s", exc)
        return {"follow_up_suggestions": _GENERIC_FOLLOWUPS}


# ─────────────────────────────────────────────────────────────────────────────
# 10. Build Final Response
# ─────────────────────────────────────────────────────────────────────────────

async def build_response_node(state: AgentState) -> dict:
    """Assemble the final response payload from all accumulated state."""
    settings = get_settings()

    # Prepare result data as a list of dicts for JSON serialization
    result_data: list[dict[str, Any]] = []
    df = state.get("query_result")
    if df is not None and not df.empty:
        result_data = df.head(settings.max_result_rows).to_dict(orient="records")

    # If there's still an unresolved SQL error, surface it in plain_english
    plain_english = state.get("plain_english_answer", "")
    if state.get("sql_error") and not plain_english:
        plain_english = (
            f"I wasn't able to execute the query successfully after "
            f"{state.get('retry_count', 0)} attempts. "
            f"Error: {state['sql_error']}"
        )

    final: dict[str, Any] = {
        "sql_generated": state.get("generated_sql", ""),
        "result_table": result_data,
        "plain_english": plain_english,
        "chart_suggestion": state.get("chart_suggestion"),
        "follow_up_suggestions": state.get("follow_up_suggestions", []),
        "retry_count": state.get("retry_count", 0),
        "execution_time_ms": round(time.time() * 1000 - state.get("execution_time_ms", 0)),
        "session_id": state.get("session_id", ""),
    }

    logger.info(
        "Final response assembled — %d result rows, %d retries, %.0fms total.",
        len(result_data),
        final["retry_count"],
        final["execution_time_ms"],
    )
    return {"final_response": final}


# ─────────────────────────────────────────────────────────────────────────────
# 11. Abort Response (Safety Refusal)
# ─────────────────────────────────────────────────────────────────────────────

async def abort_response_node(state: AgentState) -> dict:
    """Build a refusal response when the generated SQL fails safety checks."""
    reason = state.get("safety_reason", "Query blocked by safety validator.")
    logger.warning("Aborting query — safety refusal: %s", reason)

    final: dict[str, Any] = {
        "sql_generated": state.get("generated_sql", ""),
        "result_table": [],
        "plain_english": (
            f"I'm unable to execute this query because it was flagged by our safety system: "
            f"{reason}. Please rephrase your question to use only read operations."
        ),
        "chart_suggestion": None,
        "follow_up_suggestions": [
            "Can you rephrase your question as a data lookup?",
            "What data would you like to explore instead?",
            "Can you ask about a specific metric or summary?",
        ],
        "retry_count": state.get("retry_count", 0),
        "execution_time_ms": round(time.time() * 1000 - state.get("execution_time_ms", 0)),
        "session_id": state.get("session_id", ""),
    }

    return {"final_response": final}
