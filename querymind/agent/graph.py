"""LangGraph StateGraph wiring for the QueryMind agentic pipeline.

Constructs a directed graph of async node functions with conditional edges
for safety gating and error-driven retry loops.  The compiled graph is
cached at module level for reuse across requests.

Flow overview::

    load_schema → generate_sql → validate_safety
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                     execute_sql            abort_response → END
                          │
                     check_error
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
          fix_sql   build_response  interpret_result
              │           │           │
              └──► execute_sql       suggest_chart
                          │           │
                          ▼      suggest_followups
                         END          │
                              build_response → END
"""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import (
    load_schema_node,
    generate_sql_node,
    validate_safety_node,
    execute_sql_node,
    fix_sql_node,
    interpret_result_node,
    suggest_chart_node,
    suggest_followups_node,
    build_response_node,
    abort_response_node,
)
from config import get_settings

logger = logging.getLogger(__name__)

# Module-level cache for the compiled graph
_compiled_graph = None


# ─────────────────────────────────────────────────────────────────────────────
# Graph Construction
# ─────────────────────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """Construct the QueryMind agentic pipeline as a LangGraph StateGraph.

    The graph encodes the full lifecycle of a user query:

    1. **Schema loading** — introspect the DB and filter relevant tables.
    2. **SQL generation** — ask the LLM to write a SELECT query.
    3. **Safety validation** — block non-SELECT / injection attempts.
    4. **Execution** — run the query against the database.
    5. **Error check & retry** — self-correct up to ``max_retries`` times.
    6. **Post-processing** — interpret results, suggest charts, follow-ups.
    7. **Response assembly** — pack everything into the final payload.
    """
    workflow = StateGraph(AgentState)

    # ── Register all nodes ───────────────────────────────────────────────
    workflow.add_node("load_schema", load_schema_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_safety", validate_safety_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("fix_sql", fix_sql_node)
    workflow.add_node("interpret_result", interpret_result_node)
    workflow.add_node("suggest_chart", suggest_chart_node)
    workflow.add_node("suggest_followups", suggest_followups_node)
    workflow.add_node("build_response", build_response_node)
    workflow.add_node("abort_response", abort_response_node)

    # ── Entry point ──────────────────────────────────────────────────────
    workflow.set_entry_point("load_schema")

    # ── Linear edges: schema → SQL generation → safety ───────────────────
    workflow.add_edge("load_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate_safety")

    # ── Conditional: safety gate ─────────────────────────────────────────
    # Safe queries proceed to execution; unsafe ones are immediately refused.
    workflow.add_conditional_edges(
        "validate_safety",
        lambda state: "execute_sql" if state.get("is_safe", False) else "abort_response",
    )

    # ── Execution conditionally routes to fix, interpret, or error summary ──

    # ── Conditional: error check with retry logic ────────────────────────
    def route_after_error_check(state: AgentState) -> str:
        """Decide the next step after SQL execution.

        - If there's an error and retries remain → fix_sql (self-correction loop).
        - If there's an error but retries exhausted → build_response (error summary).
        - If no error → interpret_result (happy path).
        """
        settings = get_settings()
        has_error = bool(state.get("sql_error"))
        retries_remaining = state.get("retry_count", 0) < settings.max_retries

        if has_error and retries_remaining:
            logger.info(
                "SQL error detected, routing to fix_sql (retry %d/%d).",
                state.get("retry_count", 0) + 1,
                settings.max_retries,
            )
            return "fix_sql"

        if has_error:
            logger.warning(
                "SQL error persists after %d retries — building error response.",
                state.get("retry_count", 0),
            )
            return "build_response"

        return "interpret_result"

    workflow.add_conditional_edges("execute_sql", route_after_error_check)

    # ── Fix SQL loops back to execute ────────────────────────────────────
    workflow.add_edge("fix_sql", "execute_sql")

    # ── Linear post-processing pipeline ──────────────────────────────────
    workflow.add_edge("interpret_result", "suggest_chart")
    workflow.add_edge("suggest_chart", "suggest_followups")
    workflow.add_edge("suggest_followups", "build_response")

    # ── Terminal edges ───────────────────────────────────────────────────
    workflow.add_edge("build_response", END)
    workflow.add_edge("abort_response", END)

    return workflow


# ─────────────────────────────────────────────────────────────────────────────
# Compiled Graph Singleton
# ─────────────────────────────────────────────────────────────────────────────

def get_compiled_graph():
    """Get the compiled LangGraph agent.  Cached after first call.

    Returns the compiled ``Runnable`` that can be invoked with an initial
    ``AgentState`` dict::

        graph = get_compiled_graph()
        result = await graph.ainvoke(initial_state)
    """
    global _compiled_graph

    if _compiled_graph is None:
        workflow = build_graph()
        _compiled_graph = workflow.compile()
        logger.info("LangGraph agent compiled successfully.")

    return _compiled_graph
