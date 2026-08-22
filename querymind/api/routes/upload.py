"""Dataset upload endpoint for CSV and Excel files."""

import io
import logging
import re
from typing import Any
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from db.connection import get_engine
from core.schema_loader import invalidate_schema_cache
from api.routes.schema import _questions_cache

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit


class ColumnInfo(BaseModel):
    name: str
    type: str


class UploadResponse(BaseModel):
    status: str
    message: str
    table_name: str
    row_count: int
    column_count: int
    columns: list[ColumnInfo]
    preview: list[dict[str, Any]]


def _sanitize_name(raw_name: str, default_prefix: str = "dataset") -> str:
    """Sanitize table or column name for safe SQL use."""
    cleaned = raw_name.strip().lower()
    # Remove file extensions if present
    cleaned = re.sub(r"\.(csv|xlsx|xls|tsv|txt)$", "", cleaned, flags=re.IGNORECASE)
    # Replace spaces, hyphens, and dots with underscores
    cleaned = re.sub(r"[\s\-\.]+", "_", cleaned)
    # Remove any character that is not alphanumeric or underscore
    cleaned = re.sub(r"[^\w]", "", cleaned)
    # Ensure it starts with a letter
    if not cleaned or not cleaned[0].isalpha():
        cleaned = f"{default_prefix}_{cleaned}"
    # Truncate to 48 characters
    cleaned = cleaned[:48].strip("_")
    return cleaned or default_prefix


def _sanitize_columns(columns: list[str]) -> list[str]:
    """Ensure all column names are unique and valid SQL identifiers."""
    seen: dict[str, int] = {}
    clean_cols: list[str] = []

    for i, col in enumerate(columns):
        clean = _sanitize_name(str(col), default_prefix=f"col_{i+1}")
        if clean in seen:
            seen[clean] += 1
            clean = f"{clean}_{seen[clean]}"
        else:
            seen[clean] = 1
        clean_cols.append(clean)

    return clean_cols


@router.post(
    "/upload-csv",
    response_model=UploadResponse,
    tags=["Upload"],
)
async def upload_csv_or_excel(
    file: UploadFile = File(...),
    table_name: str = Form(None),
) -> UploadResponse:
    """Upload a CSV or Excel file and save it as a new database table."""
    filename = file.filename or "uploaded_data.csv"
    ext = filename.split(".")[-1].lower()

    if ext not in ("csv", "tsv", "txt", "xlsx", "xls"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Unsupported file format '.{ext}'. Supported formats: .csv, .tsv, .xlsx, .xls",
                "error_code": "INVALID_FORMAT",
            },
        )

    # 1. Read file contents into memory with size check
    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "error": f"File size ({len(contents) / (1024*1024):.1f}MB) exceeds the 15MB limit.",
                    "error_code": "FILE_TOO_LARGE",
                },
            )
        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail={"error": "The uploaded file is empty.", "error_code": "EMPTY_FILE"},
            )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to read uploaded file: {exc}")
        raise HTTPException(
            status_code=400,
            detail={"error": f"Could not read file: {str(exc)}", "error_code": "READ_ERROR"},
        )

    # 2. Parse file using pandas
    try:
        buf = io.BytesIO(contents)
        if ext in ("xlsx", "xls"):
            df = pd.read_excel(buf)
        elif ext == "tsv":
            df = pd.read_csv(buf, sep="\t")
        else:
            # Standard CSV with auto-separator detection
            try:
                df = pd.read_csv(buf)
            except Exception:
                buf.seek(0)
                df = pd.read_csv(buf, sep=None, engine="python")

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail={"error": "The uploaded dataset contains no rows.", "error_code": "EMPTY_DATASET"},
            )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to parse dataset with pandas: {exc}")
        raise HTTPException(
            status_code=400,
            detail={"error": f"Could not parse data file: {str(exc)}", "error_code": "PARSE_ERROR"},
        )

    # 3. Clean table and column names
    target_table = _sanitize_name(table_name or filename, default_prefix="user_dataset")
    df.columns = _sanitize_columns(list(df.columns))

    # Format column info for metadata
    columns_info: list[ColumnInfo] = []
    for col_name, dtype in zip(df.columns, df.dtypes):
        type_str = "INTEGER" if "int" in str(dtype) else "DECIMAL" if "float" in str(dtype) else "TIMESTAMP" if "datetime" in str(dtype) else "VARCHAR"
        columns_info.append(ColumnInfo(name=col_name, type=type_str))

    # 4. Save DataFrame into Database
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(
                lambda sync_conn: df.to_sql(
                    target_table,
                    sync_conn,
                    if_exists="replace",
                    index=False,
                )
            )

        logger.info(
            f"Successfully uploaded dataset: table='{target_table}', rows={len(df)}, columns={len(df.columns)}"
        )

        # 5. Invalidate schema and suggested questions cache
        invalidate_schema_cache()
        _questions_cache["questions"] = []
        _questions_cache["timestamp"] = 0.0

    except Exception as exc:
        logger.error(f"Failed to save DataFrame into database: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Failed to create database table '{target_table}': {str(exc)}",
                "error_code": "DB_SAVE_ERROR",
            },
        )

    # Prepare preview records (first 5 rows)
    preview_records = df.head(5).fillna("—").to_dict(orient="records")

    return UploadResponse(
        status="success",
        message=f"Successfully created table '{target_table}' with {len(df):,} rows.",
        table_name=target_table,
        row_count=len(df),
        column_count=len(df.columns),
        columns=columns_info,
        preview=preview_records,
    )
