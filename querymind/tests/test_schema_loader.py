"""Tests for the schema loader — format and filtering logic."""

import pytest
from core.schema_loader import format_schema_context, get_relevant_tables


class TestFormatSchemaContext:
    """Test schema → prompt-string formatting."""

    def test_formats_table_with_columns(self, mock_schema):
        context = format_schema_context(mock_schema)
        assert "customers" in context
        assert "id" in context

    def test_includes_foreign_keys(self, mock_schema):
        context = format_schema_context(mock_schema)
        assert "customer_id" in context

    def test_empty_schema_returns_empty_or_message(self):
        context = format_schema_context({"tables": {}})
        # Should be empty or contain a "no tables" notice — never crash
        assert isinstance(context, str)

    def test_all_tables_present(self, mock_schema):
        context = format_schema_context(mock_schema)
        for table_name in mock_schema["tables"]:
            assert table_name in context


class TestGetRelevantTables:
    """Test keyword-based table filtering."""

    @pytest.mark.asyncio
    async def test_filters_relevant_tables(self, mock_schema):
        result = await get_relevant_tables(
            mock_schema, "What are the top customers?"
        )
        assert "customers" in result.get("tables", {})

    @pytest.mark.asyncio
    async def test_includes_related_tables(self, mock_schema):
        result = await get_relevant_tables(
            mock_schema, "Show me order items with products"
        )
        tables = result.get("tables", {})
        assert "order_items" in tables or "products" in tables

    @pytest.mark.asyncio
    async def test_respects_top_k(self, mock_schema):
        result = await get_relevant_tables(mock_schema, "everything", top_k=2)
        assert len(result.get("tables", {})) <= 2

    @pytest.mark.asyncio
    async def test_empty_question_returns_tables(self, mock_schema):
        result = await get_relevant_tables(mock_schema, "", top_k=10)
        assert len(result.get("tables", {})) > 0
