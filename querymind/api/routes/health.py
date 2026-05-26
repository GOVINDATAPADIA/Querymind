"""Health check endpoint."""

import logging
from fastapi import APIRouter
from api.models.response import HealthResponse
from db.connection import check_db_health
from services.llm_provider import check_llm_health

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Check the health of the API, database, and LLM connections."""
    db_ok = False
    llm_ok = False

    try:
        db_ok = await check_db_health()
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")

    try:
        llm_ok = await check_llm_health()
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")

    status = "ok" if db_ok else "degraded"

    return HealthResponse(
        status=status,
        db_connected=db_ok,
        llm_connected=llm_ok,
    )
