"""Main query endpoint — natural language to SQL pipeline."""

import time
import uuid
import logging
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

from api.models.request import QueryRequest
from api.models.response import QueryResponse, ErrorResponse
from agent.graph import get_compiled_graph
from core.memory_manager import memory_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    tags=["Query"],
)
async def run_query(
    request: QueryRequest,
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
) -> QueryResponse | JSONResponse:
    """Execute a natural language query against the connected database.

    The full LangGraph pipeline runs: schema introspection → SQL generation →
    safety validation → execution (with self-correction) → interpretation →
    chart suggestion → follow-up generation.
    """
    start_time = time.time()

    # Auto-generate session ID if the caller didn't supply one
    session_id = x_session_id or str(uuid.uuid4())

    try:
        # Pull conversation history so follow-up questions resolve correctly
        history = memory_manager.get_history(session_id)

        # Build the initial agent state dict expected by the LangGraph pipeline
        initial_state = {
            "user_question": request.question,
            "conversation_history": history,
            "schema_context": "",
            "generated_sql": "",
            "sql_error": None,
            "query_result": None,
            "result_truncated": False,
            "retry_count": 0,
            "is_safe": True,
            "safety_reason": "",
            "plain_english_answer": "",
            "chart_suggestion": None,
            "follow_up_suggestions": [],
            "final_response": None,
            "session_id": session_id,
            "execution_time_ms": time.time() * 1000,  # start ts for duration calc
        }

        # Run the compiled LangGraph agent
        graph = get_compiled_graph()
        result = await graph.ainvoke(initial_state)

        final = result.get("final_response", {})

        # Persist the turn in conversational memory
        memory_manager.add_interaction(
            session_id,
            request.question,
            final.get("plain_english", ""),
        )

        response = QueryResponse(
            sql_generated=final.get("sql_generated", ""),
            result_table=final.get("result_table", []),
            plain_english=final.get("plain_english", ""),
            chart_suggestion=final.get("chart_suggestion"),
            follow_up_suggestions=final.get("follow_up_suggestions", []),
            retry_count=final.get("retry_count", 0),
            execution_time_ms=round((time.time() - start_time) * 1000),
            session_id=session_id,
        )

        logger.info(
            "Query completed",
            extra={
                "session_id": session_id,
                "question": request.question[:100],
                "retry_count": response.retry_count,
                "execution_time_ms": response.execution_time_ms,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Query pipeline failed: {e}", exc_info=True)

        # Surface a connection-specific 503 so callers know to retry
        if "connection" in str(e).lower() or "database" in str(e).lower():
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Database connection failed",
                    "error_code": "DB_CONNECTION_ERROR",
                    "suggestion": "Please try again in a few moments",
                },
                headers={"Retry-After": "5"},
            )

        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred while processing your query",
                "error_code": "PIPELINE_ERROR",
                "suggestion": "Try rephrasing your question or simplifying it",
            },
        )
