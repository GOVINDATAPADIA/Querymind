"""Translate a SQL query result (DataFrame) into a plain-English interpretation.

Uses the configured LLM via ``get_llm()`` and falls back to a basic summary
string if the LLM call fails for any reason.
"""

import logging

import pandas as pd

from services.llm_provider import get_llm
from agent.prompts import RESULT_INTERPRETATION_PROMPT

logger = logging.getLogger(__name__)


def _build_result_summary(df: pd.DataFrame) -> str:
    """Create a compact textual summary of a DataFrame for LLM consumption."""

    if df is None or df.empty:
        return "The query returned no results."

    if len(df) == 1:
        # Single-row result → key: value pairs
        pairs = [f"  {col}: {df.iloc[0][col]}" for col in df.columns]
        return "Single-row result:\n" + "\n".join(pairs)

    # Multi-row result
    parts: list[str] = []
    parts.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    parts.append(f"Columns: {', '.join(df.columns.tolist())}")
    parts.append(f"\nFirst 5 rows:\n{df.head(5).to_string(index=False)}")

    # Basic stats for numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        stats = df[numeric_cols].describe().to_string()
        parts.append(f"\nNumeric column statistics:\n{stats}")

    return "\n".join(parts)


def _basic_fallback_summary(question: str, df: pd.DataFrame) -> str:
    """Minimal plain-English summary when the LLM is unavailable."""

    if df is None or df.empty:
        return (
            "The query returned no results. This may mean no data matched "
            "your criteria — try broadening your filters."
        )

    if len(df) == 1 and len(df.columns) == 1:
        value = df.iloc[0, 0]
        col = df.columns[0]
        return f"The result is {value} ({col})."

    if len(df) == 1:
        pairs = ", ".join(
            f"{col} = {df.iloc[0][col]}" for col in df.columns
        )
        return f"The query returned a single record: {pairs}."

    return (
        f"The query returned {len(df)} rows across "
        f"{len(df.columns)} columns ({', '.join(df.columns.tolist())})."
    )


async def interpret_result(
    question: str,
    sql: str,
    df: pd.DataFrame,
) -> str:
    """Produce a plain-English interpretation of *df*.

    Parameters
    ----------
    question:
        The original user question that triggered the query.
    sql:
        The SQL statement that was executed.
    df:
        The result DataFrame (may be empty).

    Returns
    -------
    str
        A concise, non-technical explanation of the query results.
        Falls back to a basic summary if the LLM call fails.
    """
    result_summary = _build_result_summary(df)

    try:
        llm = get_llm()
        chain = RESULT_INTERPRETATION_PROMPT | llm
        response = await chain.ainvoke({
            "question": question,
            "sql": sql,
            "result_summary": result_summary,
        })
        return response.content.strip()
    except Exception as exc:
        logger.warning(
            "LLM interpretation failed (%s); using fallback summary.", exc
        )
        return _basic_fallback_summary(question, df)
