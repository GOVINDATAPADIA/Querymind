"""Tests for the LangGraph agent pipeline — nodes and routing."""

import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch


class TestNodeFunctions:
    """Test individual graph node functions with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_validate_safety_blocks_unsafe_sql(self):
        """Unsafe SQL is flagged without any DB or LLM interaction."""
        from agent.nodes import validate_safety_node

        state = {
            "generated_sql": "DROP TABLE customers",
            "is_safe": True,
            "safety_reason": "",
        }
        result = await validate_safety_node(state)
        assert result["is_safe"] is False
        assert result["safety_reason"] != ""

    @pytest.mark.asyncio
    async def test_validate_safety_allows_select(self):
        """A plain SELECT should pass validation."""
        from agent.nodes import validate_safety_node

        state = {
            "generated_sql": "SELECT name FROM customers",
            "is_safe": True,
            "safety_reason": "",
        }
        result = await validate_safety_node(state)
        assert result["is_safe"] is True

    @pytest.mark.asyncio
    async def test_suggest_chart_bar(self, sample_dataframe):
        """Categorical + numeric data should yield a bar chart."""
        from agent.nodes import suggest_chart_node

        state = {
            "query_result": sample_dataframe,
            "user_question": "Top products by revenue",
        }
        result = await suggest_chart_node(state)
        assert result["chart_suggestion"] is not None
        assert result["chart_suggestion"]["type"] == "bar"

    @pytest.mark.asyncio
    async def test_suggest_chart_line(self, time_series_dataframe):
        """Datetime + numeric data should yield a line chart."""
        from agent.nodes import suggest_chart_node

        state = {
            "query_result": time_series_dataframe,
            "user_question": "Revenue over time",
        }
        result = await suggest_chart_node(state)
        assert result["chart_suggestion"] is not None
        assert result["chart_suggestion"]["type"] == "line"

    @pytest.mark.asyncio
    async def test_suggest_chart_empty(self, empty_dataframe):
        """Empty result should yield no chart."""
        from agent.nodes import suggest_chart_node

        state = {
            "query_result": empty_dataframe,
            "user_question": "Find something",
        }
        result = await suggest_chart_node(state)
        assert result["chart_suggestion"] is None

    @pytest.mark.asyncio
    async def test_suggest_chart_stat_card(self, single_value_dataframe):
        """Single aggregated value should yield a stat_card."""
        from agent.nodes import suggest_chart_node

        state = {
            "query_result": single_value_dataframe,
            "user_question": "What is total revenue?",
        }
        result = await suggest_chart_node(state)
        assert result["chart_suggestion"] is not None
        assert result["chart_suggestion"]["type"] == "stat_card"

    @pytest.mark.asyncio
    @patch("agent.nodes.get_engine")
    @patch("agent.nodes.execute_query")
    async def test_execute_sql_node_success(
        self, mock_exec, mock_engine, sample_dataframe
    ):
        """Successful query returns DataFrame and no error."""
        from agent.nodes import execute_sql_node

        mock_engine.return_value = MagicMock()
        mock_exec.return_value = (sample_dataframe, None)

        state = {"generated_sql": "SELECT * FROM products LIMIT 5"}
        result = await execute_sql_node(state)

        assert result["sql_error"] is None
        assert result["query_result"] is not None
        assert len(result["query_result"]) == 5

    @pytest.mark.asyncio
    @patch("agent.nodes.get_engine")
    @patch("agent.nodes.execute_query")
    async def test_execute_sql_node_error(self, mock_exec, mock_engine):
        """Failed query surfaces the error string."""
        from agent.nodes import execute_sql_node

        mock_engine.return_value = MagicMock()
        mock_exec.return_value = (pd.DataFrame(), "relation 'xyz' does not exist")

        state = {"generated_sql": "SELECT * FROM xyz"}
        result = await execute_sql_node(state)

        assert result["sql_error"] is not None
        assert "does not exist" in result["sql_error"]

    @pytest.mark.asyncio
    async def test_build_response_node(self, sample_dataframe):
        """Build response assembles all fields correctly."""
        from agent.nodes import build_response_node

        state = {
            "generated_sql": "SELECT * FROM products",
            "query_result": sample_dataframe,
            "plain_english_answer": "Here are the top products.",
            "chart_suggestion": {"type": "bar"},
            "follow_up_suggestions": ["What else?"],
            "retry_count": 0,
            "execution_time_ms": 0.0,
            "session_id": "test-123",
            "sql_error": None,
        }
        result = await build_response_node(state)
        final = result["final_response"]

        assert final is not None
        assert final["sql_generated"] == "SELECT * FROM products"
        assert len(final["result_table"]) > 0
        assert final["session_id"] == "test-123"

    @pytest.mark.asyncio
    async def test_abort_response_node(self):
        """Abort response returns a refusal message."""
        from agent.nodes import abort_response_node

        state = {
            "generated_sql": "DROP TABLE customers",
            "safety_reason": "DDL statement detected",
            "session_id": "test-session",
            "execution_time_ms": 0.0,
            "retry_count": 0,
        }
        result = await abort_response_node(state)
        final = result["final_response"]

        assert final is not None
        assert final["result_table"] == []
        assert "unsafe" in final["plain_english"].lower() or "blocked" in final["plain_english"].lower() or "cannot" in final["plain_english"].lower()


class TestGraphRouting:
    """Test the graph's conditional routing logic."""

    @pytest.mark.asyncio
    @patch("agent.nodes.get_engine")
    @patch("agent.nodes.get_cached_schema")
    @patch("agent.nodes.get_relevant_tables")
    @patch("agent.nodes.format_schema_context")
    @patch("agent.nodes.get_llm")
    @patch("agent.nodes.execute_query")
    async def test_happy_path_full_graph(
        self,
        mock_execute,
        mock_get_llm,
        mock_format,
        mock_relevant,
        mock_schema,
        mock_engine,
        sample_dataframe,
        mock_schema as schema_fixture,
    ):
        """End-to-end: question → SQL → execute → interpret → response."""
        mock_engine.return_value = MagicMock()
        mock_schema.return_value = schema_fixture
        mock_relevant.return_value = schema_fixture
        mock_format.return_value = "Table: products\nColumns: id, name, price"

        # LLM returns different content depending on which prompt calls it
        sql_resp = MagicMock(content="SELECT name, price FROM products LIMIT 5")
        interp_resp = MagicMock(content="Top 5 products listed by price.")
        followup_resp = MagicMock(
            content='["Break down by category?", "Compare to last quarter?", "Show margins?"]'
        )

        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(
            side_effect=[sql_resp, interp_resp, followup_resp]
        )

        mock_llm_instance = MagicMock()
        mock_llm_instance.__or__ = MagicMock(return_value=mock_chain)
        mock_get_llm.return_value = mock_llm_instance

        mock_execute.return_value = (sample_dataframe, None)

        with patch("agent.nodes.SQL_GENERATION_PROMPT") as p1, \
             patch("agent.nodes.RESULT_INTERPRETATION_PROMPT") as p2, \
             patch("agent.nodes.FOLLOWUP_PROMPT") as p3:
            p1.__or__ = MagicMock(return_value=mock_chain)
            p2.__or__ = MagicMock(return_value=mock_chain)
            p3.__or__ = MagicMock(return_value=mock_chain)

            from agent.graph import build_graph

            workflow = build_graph()
            graph = workflow.compile()

            result = await graph.ainvoke(
                {
                    "user_question": "Top 5 products by price?",
                    "conversation_history": [],
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
                    "session_id": "test-session",
                    "execution_time_ms": 0.0,
                }
            )

        assert result["final_response"] is not None
        assert result["is_safe"] is True
        assert result["retry_count"] == 0
