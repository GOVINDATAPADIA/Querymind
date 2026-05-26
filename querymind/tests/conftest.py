"""Shared test fixtures for the QueryMind test suite."""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock

# Ensure project root is on sys.path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test-safe environment variables before any app module is imported
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("LLM_PROVIDER", "openai")
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-real")
os.environ.setdefault("LOG_LEVEL", "WARNING")


# ── DataFrame fixtures ────────────────────────────────────────────


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Categorical + numeric data — should trigger a bar chart suggestion."""
    return pd.DataFrame(
        {
            "product": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E"],
            "revenue": [15000.50, 12300.00, 9800.75, 8500.00, 7200.25],
            "quantity": [150, 123, 98, 85, 72],
        }
    )


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """An empty DataFrame for testing empty-result handling."""
    return pd.DataFrame()


@pytest.fixture
def single_value_dataframe() -> pd.DataFrame:
    """Single aggregated value — should trigger a stat_card suggestion."""
    return pd.DataFrame({"total_revenue": [152800.50]})


@pytest.fixture
def time_series_dataframe() -> pd.DataFrame:
    """Datetime + numeric — should trigger a line chart suggestion."""
    return pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"]
            ),
            "revenue": [10000, 12000, 11500, 13000],
        }
    )


# ── Mock helpers ──────────────────────────────────────────────────


@pytest.fixture
def mock_llm():
    """A mock LLM that returns a predictable SQL SELECT response."""
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(
        return_value=MagicMock(
            content=(
                "SELECT p.name, SUM(oi.quantity * oi.unit_price) AS revenue "
                "FROM products p JOIN order_items oi ON p.id = oi.product_id "
                "GROUP BY p.name ORDER BY revenue DESC LIMIT 5"
            )
        )
    )
    return llm


@pytest.fixture
def mock_schema() -> dict:
    """A realistic e-commerce schema dict matching the loader's output format."""
    return {
        "tables": {
            "customers": {
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "email", "type": "VARCHAR"},
                    {"name": "region", "type": "VARCHAR"},
                ],
                "primary_keys": ["id"],
                "foreign_keys": [],
            },
            "orders": {
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "customer_id", "type": "INTEGER"},
                    {"name": "order_date", "type": "DATE"},
                    {"name": "total_amount", "type": "DECIMAL"},
                ],
                "primary_keys": ["id"],
                "foreign_keys": [
                    {
                        "column": "customer_id",
                        "referred_table": "customers",
                        "referred_column": "id",
                    }
                ],
            },
            "products": {
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "category", "type": "VARCHAR"},
                    {"name": "price", "type": "DECIMAL"},
                ],
                "primary_keys": ["id"],
                "foreign_keys": [],
            },
            "order_items": {
                "columns": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "order_id", "type": "INTEGER"},
                    {"name": "product_id", "type": "INTEGER"},
                    {"name": "quantity", "type": "INTEGER"},
                    {"name": "unit_price", "type": "DECIMAL"},
                ],
                "primary_keys": ["id"],
                "foreign_keys": [
                    {
                        "column": "order_id",
                        "referred_table": "orders",
                        "referred_column": "id",
                    },
                    {
                        "column": "product_id",
                        "referred_table": "products",
                        "referred_column": "id",
                    },
                ],
            },
        }
    }
