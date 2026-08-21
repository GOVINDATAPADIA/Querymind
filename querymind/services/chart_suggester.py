"""Pure-logic chart suggestion engine — no LLM calls.

Analyzes a DataFrame's shape and column types to recommend an appropriate
Plotly chart specification that the frontend can render directly.
"""

import pandas as pd


def _classify_columns(
    df: pd.DataFrame,
) -> tuple[list[str], list[str], list[str]]:
    """Split column names into numeric, datetime, and categorical buckets."""
    numeric_cols: list[str] = []
    datetime_cols: list[str] = []
    categorical_cols: list[str] = []

    for col in df.columns:
        dtype = df[col].dtype

        # Explicit datetime dtype
        if pd.api.types.is_datetime64_any_dtype(dtype):
            datetime_cols.append(col)
            continue

        # Numeric dtypes (int64, float64, etc.)
        if pd.api.types.is_numeric_dtype(dtype):
            numeric_cols.append(col)
            continue

        # Object / string columns — try to detect date-like strings
        if dtype == object or pd.api.types.is_string_dtype(dtype):
            sample = df[col].dropna().head(20)
            if len(sample) > 0:
                try:
                    pd.to_datetime(sample, infer_datetime_format=True)
                    datetime_cols.append(col)
                    continue
                except (ValueError, TypeError):
                    pass
            categorical_cols.append(col)
            continue

        # Fallback: treat as categorical
        categorical_cols.append(col)

    return numeric_cols, datetime_cols, categorical_cols


def _truncate_data(df: pd.DataFrame, max_rows: int = 100) -> list[dict]:
    """Return DataFrame records capped at *max_rows*."""
    return df.head(max_rows).to_dict(orient="records")


def suggest_chart(df: pd.DataFrame, question: str = "") -> dict | None:
    """Suggest a Plotly chart specification based on the DataFrame's shape.

    Returns a dict with at minimum ``type``, ``title``, and ``data`` keys,
    or ``None`` when no meaningful chart can be produced.
    """
    if df is None or df.empty or len(df) == 0:
        return None

    numeric_cols, datetime_cols, categorical_cols = _classify_columns(df)
    data = _truncate_data(df)

    # ── Single scalar value ──────────────────────────────────────────────
    if len(df) == 1 and len(df.columns) == 1:
        col_name = df.columns[0]
        value = df.iloc[0, 0]
        return {
            "type": "stat_card",
            "value": value,
            "label": col_name,
            "title": "Summary",
            "data": data,
        }

    q_lower = (question or "").lower()
    pie_keywords = ("share", "percent", "distribution", "breakdown", "proportion", "ratio", "split", "pie")

    # ── 1 datetime + 1 numeric → area / line chart ─────────────────────
    if len(datetime_cols) >= 1 and len(numeric_cols) >= 1:
        x_col = datetime_cols[0]
        y_col = numeric_cols[0]
        chart_type = "area" if "area" in q_lower else "line"
        return {
            "type": chart_type,
            "x": x_col,
            "y": y_col,
            "columns": [x_col, y_col],
            "title": f"{y_col.replace('_', ' ').title()} over time ({x_col})",
            "data": data,
        }

    # ── 1 categorical + 1 numeric → bar or pie chart ────────────────────
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        
        # Suggest pie chart if small set of categories and asks for share/breakdown
        if (len(df) <= 6 and any(k in q_lower for k in pie_keywords)) or (len(df) <= 5 and "category" in x_col.lower()):
            return {
                "type": "pie",
                "x": x_col,
                "y": y_col,
                "nameKey": x_col,
                "dataKey": y_col,
                "columns": [x_col, y_col],
                "title": f"{y_col.replace('_', ' ').title()} Distribution by {x_col.replace('_', ' ').title()}",
                "data": data,
            }

        return {
            "type": "bar",
            "x": x_col,
            "y": y_col,
            "columns": [x_col, y_col],
            "title": f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
            "data": data,
        }

    # ── 1 categorical + 2+ numeric → multi-bar chart ────────────────────
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 2:
        x_col = categorical_cols[0]
        return {
            "type": "bar",
            "x": x_col,
            "y": numeric_cols[0],
            "y_series": numeric_cols[:3],
            "columns": [x_col] + numeric_cols[:3],
            "title": f"Metrics by {x_col.replace('_', ' ').title()}",
            "data": data,
        }

    # ── 2+ numeric → scatter plot ────────────────────────────────────────
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        return {
            "type": "bar",
            "x": x_col,
            "y": y_col,
            "columns": [x_col, y_col],
            "title": f"{y_col} vs {x_col}",
            "data": data,
        }

    # ── Fallback: table view ─────────────────────────────────────────────
    all_cols = list(df.columns)
    return {
        "type": "table",
        "columns": all_cols if len(all_cols) >= 1 else list(df.columns),
        "title": "Query Results",
        "data": data,
    }
