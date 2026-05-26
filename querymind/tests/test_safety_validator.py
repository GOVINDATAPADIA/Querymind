"""Tests for the SQL safety validator — 17 test cases covering all threat categories."""

import pytest
from core.safety_validator import validate_sql, sanitize_sql_output


class TestValidateSQL:
    """Verify that SAFE queries pass and UNSAFE queries are blocked."""

    # ── SAFE queries ────────────────────────────────────────────

    def test_simple_select(self):
        result = validate_sql("SELECT * FROM customers")
        assert result.is_safe is True

    def test_select_with_where(self):
        result = validate_sql(
            "SELECT name, email FROM customers WHERE region = 'North America'"
        )
        assert result.is_safe is True

    def test_select_with_join(self):
        result = validate_sql(
            "SELECT c.name, o.total_amount "
            "FROM customers c JOIN orders o ON c.id = o.customer_id"
        )
        assert result.is_safe is True

    def test_select_with_aggregation(self):
        result = validate_sql(
            "SELECT category, COUNT(*) AS cnt, AVG(price) AS avg_price "
            "FROM products GROUP BY category ORDER BY cnt DESC"
        )
        assert result.is_safe is True

    def test_select_with_subquery(self):
        result = validate_sql(
            "SELECT name FROM customers WHERE id IN "
            "(SELECT customer_id FROM orders WHERE total_amount > 1000)"
        )
        assert result.is_safe is True

    # ── DDL (should block) ──────────────────────────────────────

    def test_drop_table(self):
        result = validate_sql("DROP TABLE customers")
        assert result.is_safe is False
        assert result.risk_level == "critical"

    def test_alter_table(self):
        result = validate_sql(
            "ALTER TABLE customers ADD COLUMN hacked VARCHAR(100)"
        )
        assert result.is_safe is False

    def test_truncate(self):
        result = validate_sql("TRUNCATE TABLE customers")
        assert result.is_safe is False

    def test_create_table(self):
        result = validate_sql("CREATE TABLE hacked (id INT)")
        assert result.is_safe is False

    # ── DML writes (should block) ───────────────────────────────

    def test_delete_from(self):
        result = validate_sql("DELETE FROM customers WHERE id = 1")
        assert result.is_safe is False

    def test_update_table(self):
        result = validate_sql(
            "UPDATE customers SET name = 'hacked' WHERE id = 1"
        )
        assert result.is_safe is False

    def test_insert_into(self):
        result = validate_sql(
            "INSERT INTO customers (name, email) VALUES ('test', 'test@test.com')"
        )
        assert result.is_safe is False

    # ── Injection patterns (should block) ───────────────────────

    def test_union_injection(self):
        result = validate_sql(
            "SELECT name FROM customers UNION SELECT password FROM users"
        )
        assert result.is_safe is False

    def test_stacked_queries(self):
        result = validate_sql("SELECT * FROM customers; DROP TABLE customers")
        assert result.is_safe is False

    def test_comment_injection(self):
        result = validate_sql("SELECT * FROM customers -- WHERE id = 1")
        assert result.is_safe is False

    def test_exec_command(self):
        result = validate_sql("EXEC xp_cmdshell 'dir'")
        assert result.is_safe is False

    def test_into_outfile(self):
        result = validate_sql(
            "SELECT * FROM customers INTO OUTFILE '/tmp/data.csv'"
        )
        assert result.is_safe is False


class TestSanitizeSQLOutput:
    """Verify LLM output cleanup."""

    def test_strip_markdown_code_fence(self):
        raw = "```sql\nSELECT * FROM customers\n```"
        assert sanitize_sql_output(raw) == "SELECT * FROM customers"

    def test_strip_backticks(self):
        raw = "`SELECT * FROM customers`"
        assert sanitize_sql_output(raw) == "SELECT * FROM customers"

    def test_strip_whitespace(self):
        raw = "  \n  SELECT * FROM customers  \n  "
        assert sanitize_sql_output(raw) == "SELECT * FROM customers"

    def test_clean_sql_passthrough(self):
        raw = "SELECT * FROM customers"
        assert sanitize_sql_output(raw) == "SELECT * FROM customers"

    def test_strip_trailing_semicolon(self):
        raw = "SELECT * FROM customers;"
        result = sanitize_sql_output(raw)
        assert not result.endswith(";")
