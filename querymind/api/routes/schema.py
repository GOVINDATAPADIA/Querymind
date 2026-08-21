"""Schema introspection and suggested questions endpoints."""

import json
import logging
import re
import time
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.models.response import SchemaResponse, SchemaTable, ErrorResponse
from db.connection import get_engine
from core.schema_loader import get_cached_schema, format_schema_context
from services.llm_provider import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache for suggested questions: {"questions": [...], "timestamp": 0.0}
_questions_cache: dict[str, Any] = {
    "questions": [],
    "timestamp": 0.0,
}


class QuestionItem(BaseModel):
    text: str
    category: str


class SuggestedQuestionsResponse(BaseModel):
    questions: list[QuestionItem]


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


def _generate_fallback_questions(tables_dict: dict[str, Any]) -> list[dict[str, str]]:
    """Build intelligent fallback questions directly from table and column names."""
    questions = []
    table_names = list(tables_dict.keys())

    for tname in table_names[:5]:
        tinfo = tables_dict.get(tname, {})
        cols = [c["name"] for c in tinfo.get("columns", [])]
        num_cols = [c["name"] for c in tinfo.get("columns", []) if any(k in c.get("type", "").lower() for k in ("int", "dec", "num", "float", "price", "amount", "cost"))]
        
        t_clean = tname.replace("_", " ").title()
        
        if num_cols:
            n_clean = num_cols[0].replace("_", " ").title()
            questions.append({
                "text": f"What are the top 5 {tname} by {n_clean}?",
                "category": t_clean
            })
        else:
            questions.append({
                "text": f"Show me all records from the {tname} table",
                "category": t_clean
            })

    if len(questions) < 5:
        defaults = [
            {"text": "Show total revenue by category", "category": "Revenue"},
            {"text": "What are the most active customers?", "category": "Customers"},
            {"text": "Compare sales across regions", "category": "Sales"},
            {"text": "List products with low inventory", "category": "Inventory"},
            {"text": "Show monthly order volume trend", "category": "Analytics"},
        ]
        for d in defaults:
            if len(questions) < 5:
                questions.append(d)

    return questions[:5]


@router.get(
    "/suggested-questions",
    response_model=SuggestedQuestionsResponse,
    tags=["Schema"],
)
async def get_suggested_questions() -> SuggestedQuestionsResponse:
    """Generate dynamic AI-suggested questions based on the live database schema."""
    global _questions_cache

    # 1. Check cache (5 min TTL)
    if _questions_cache["questions"] and (time.time() - _questions_cache["timestamp"] < 300):
        return SuggestedQuestionsResponse(questions=_questions_cache["questions"])

    try:
        engine = get_engine()
        schema = await get_cached_schema(engine)
        tables_dict = schema.get("tables", {}) if (isinstance(schema, dict) and "tables" in schema) else (schema if isinstance(schema, dict) else {})

        if not tables_dict:
            return SuggestedQuestionsResponse(questions=_generate_fallback_questions({}))

        schema_context = format_schema_context(schema)

        # 2. Call LLM with schema context
        llm = get_llm(temperature=0.3)
        system_prompt = (
            "You are a database analyst. Given the relational database schema below, "
            "suggest exactly 5 compelling, diverse, realistic business questions a user or executive would ask. "
            "Each question should explore different tables, aggregations, or rankings. "
            "Return ONLY a valid JSON array of 5 objects with 'text' and 'category' (1-word tag). "
            "Example format: [{\"text\": \"Who are the top 5 artists with the most albums?\", \"category\": \"Artists\"}]"
        )
        user_prompt = f"Database Schema:\n{schema_context}\n\nGenerate exactly 5 questions as JSON:"

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        content = response.content.strip()
        # Strip reasoning tags if present
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
        # Strip code fences if present
        if "```" in content:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, flags=re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()

        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) >= 3:
            results = [
                {"text": str(q.get("text", "")), "category": str(q.get("category", "General"))}
                for q in parsed[:5]
                if q.get("text")
            ]
            _questions_cache["questions"] = results
            _questions_cache["timestamp"] = time.time()
            return SuggestedQuestionsResponse(questions=results)

    except Exception as exc:
        logger.warning(f"AI suggested questions generation failed: {exc}, using fallback")

    # 3. Fallback
    fallback = _generate_fallback_questions(tables_dict if 'tables_dict' in locals() else {})
    _questions_cache["questions"] = fallback
    _questions_cache["timestamp"] = time.time()
    return SuggestedQuestionsResponse(questions=fallback)
