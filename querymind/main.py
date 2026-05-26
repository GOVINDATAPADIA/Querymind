"""QueryMind — Natural Language to SQL Agentic System.

FastAPI application entrypoint with structured logging, lifespan management,
CORS middleware, and global exception handlers.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pythonjsonlogger import jsonlogger

from config import get_settings
from db.connection import get_engine, dispose_engine, check_db_health
from api.routes import health, schema, query


# ── Structured JSON Logging ──────────────────────────────────────


def setup_logging() -> None:
    """Configure structured JSON logging for the entire application."""
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Quiet noisy third-party loggers
    for noisy in ("httpcore", "httpx", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# ── Lifespan ─────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle hooks."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("QueryMind starting up...")

    # Validate DB connection on startup
    try:
        get_engine()
        if await check_db_health():
            logger.info("Database connection verified")
        else:
            logger.warning("Database health check failed — running in degraded mode")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield  # ← application runs here

    # Shutdown
    logger.info("QueryMind shutting down...")
    await dispose_engine()


# ── FastAPI App ───────────────────────────────────────────────────

app = FastAPI(
    title="QueryMind",
    description="Natural Language to SQL Agentic System — ask questions in plain English, get structured answers from any relational database.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permissive for dev; tighten origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ────────────────────────────────────


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Return 422 with field-level error details for Pydantic validation failures."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "suggestion": "Check your request body and try again",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler — never expose raw stack traces to API consumers."""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "suggestion": "Please try again later",
        },
    )


# ── Register Routers ─────────────────────────────────────────────

app.include_router(health.router)
app.include_router(schema.router)
app.include_router(query.router)
