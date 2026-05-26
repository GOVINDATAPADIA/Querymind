"""SQL injection and mutation guard — defence-in-depth validation.

Combines ``sqlparse`` token analysis with regex pattern matching to ensure
only safe ``SELECT`` queries reach the database.  All blocked attempts are
logged to a dedicated ``security.log`` file.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML

# ---------------------------------------------------------------------------
# Security logger — writes exclusively to security.log
# ---------------------------------------------------------------------------
security_logger = logging.getLogger("querymind.security")
security_logger.setLevel(logging.WARNING)

_file_handler = logging.FileHandler("security.log", encoding="utf-8")
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
)
security_logger.addHandler(_file_handler)

# Prevent propagation to the root logger so security events stay isolated
security_logger.propagate = False


# ---------------------------------------------------------------------------
# Result data class
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SafetyResult:
    """Outcome of a SQL safety check."""

    is_safe: bool
    reason: str
    risk_level: str  # "safe" | "warning" | "critical"


# ---------------------------------------------------------------------------
# Blocked patterns
# ---------------------------------------------------------------------------

# DDL keywords
_DDL_KEYWORDS: set[str] = {"DROP", "CREATE", "ALTER", "TRUNCATE"}

# DML write keywords
_DML_WRITE_KEYWORDS: set[str] = {"INSERT", "UPDATE", "DELETE", "MERGE"}

# Dangerous executable / file patterns
_DANGEROUS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bEXEC\b", re.IGNORECASE),
    re.compile(r"\bEXECUTE\b", re.IGNORECASE),
    re.compile(r"\bxp_", re.IGNORECASE),
    re.compile(r"\bsp_", re.IGNORECASE),
    re.compile(r"\bINTO\s+OUTFILE\b", re.IGNORECASE),
    re.compile(r"\bLOAD_FILE\b", re.IGNORECASE),
]

# Injection patterns
_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bUNION\s+SELECT\b", re.IGNORECASE),
        "UNION SELECT injection detected",
    ),
    (
        re.compile(r";"),  # stacked queries
        "Stacked queries (semicolon) detected",
    ),
    (
        re.compile(r"--"),
        "SQL line-comment injection (--) detected",
    ),
    (
        re.compile(r"/\*"),
        "SQL block-comment injection (/*) detected",
    ),
    (
        re.compile(r"#"),
        "SQL comment injection (#) detected",
    ),
]

# System-table write guard (very broad — intentionally conservative)
_SYSTEM_TABLE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE)\b.*\binformation_schema\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE)\b.*\bpg_catalog\b",
        re.IGNORECASE | re.DOTALL,
    ),
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _log_blocked(sql: str, reason: str, risk_level: str) -> None:
    """Write a structured entry to security.log."""
    timestamp = datetime.now(timezone.utc).isoformat()
    security_logger.warning(
        "BLOCKED | risk=%s | time=%s | reason=%s | sql=%s",
        risk_level,
        timestamp,
        reason,
        sql.replace("\n", " ").strip()[:500],
    )


def _check_statement_type(parsed: list[Statement]) -> SafetyResult | None:
    """Ensure only SELECT statements are present (sqlparse token analysis)."""
    if not parsed:
        return SafetyResult(
            is_safe=False,
            reason="Empty or unparsable SQL statement.",
            risk_level="warning",
        )

    for stmt in parsed:
        # Skip empty / whitespace-only statements
        stmt_type = stmt.get_type()
        if stmt_type is None:
            # sqlparse returns None for whitespace-only fragments — allow
            continue

        if stmt_type and stmt_type.upper() != "SELECT":
            return SafetyResult(
                is_safe=False,
                reason=f"Only SELECT statements are allowed (got {stmt_type}).",
                risk_level="critical",
            )

        # Walk tokens for DDL / DML keywords that sqlparse may not surface
        for token in stmt.flatten():
            word = token.ttype
            value = token.value.upper().strip()
            if word in (Keyword, DML):
                if value in _DDL_KEYWORDS:
                    return SafetyResult(
                        is_safe=False,
                        reason=f"DDL keyword '{value}' is not allowed.",
                        risk_level="critical",
                    )
                if value in _DML_WRITE_KEYWORDS:
                    return SafetyResult(
                        is_safe=False,
                        reason=f"DML write keyword '{value}' is not allowed.",
                        risk_level="critical",
                    )

    return None  # No issues found at the token level


def _check_regex_patterns(sql: str) -> SafetyResult | None:
    """Run regex-based defence-in-depth checks."""
    sql_upper = sql.upper()

    # DDL / DML keyword check (regex layer — belt AND suspenders)
    for kw in _DDL_KEYWORDS | _DML_WRITE_KEYWORDS:
        pattern = re.compile(rf"\b{kw}\b", re.IGNORECASE)
        if pattern.search(sql):
            return SafetyResult(
                is_safe=False,
                reason=f"Blocked keyword '{kw}' detected.",
                risk_level="critical",
            )

    # Dangerous executable patterns
    for pat in _DANGEROUS_PATTERNS:
        if pat.search(sql):
            return SafetyResult(
                is_safe=False,
                reason=f"Dangerous pattern detected: {pat.pattern}",
                risk_level="critical",
            )

    # Injection patterns
    for pat, description in _INJECTION_PATTERNS:
        if pat.search(sql):
            return SafetyResult(
                is_safe=False,
                reason=description,
                risk_level="critical",
            )

    # System-table modification attempts
    for pat in _SYSTEM_TABLE_PATTERNS:
        if pat.search(sql):
            return SafetyResult(
                is_safe=False,
                reason="Modification of system tables is not allowed.",
                risk_level="critical",
            )

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_sql(sql: str) -> SafetyResult:
    """Validate a SQL string for safety.

    Only ``SELECT`` statements are permitted.  The function applies two
    independent layers of checks:

    1. **sqlparse token analysis** — structural statement-type validation.
    2. **Regex pattern matching** — catches obfuscated or edge-case attacks.

    Returns a :class:`SafetyResult` with ``is_safe=True`` only when both
    layers pass.
    """
    if not sql or not sql.strip():
        return SafetyResult(
            is_safe=False,
            reason="Empty SQL statement.",
            risk_level="warning",
        )

    cleaned = sql.strip()

    # Layer 1: sqlparse token analysis
    parsed = sqlparse.parse(cleaned)
    token_result = _check_statement_type(parsed)
    if token_result is not None and not token_result.is_safe:
        _log_blocked(cleaned, token_result.reason, token_result.risk_level)
        return token_result

    # Layer 2: regex pattern matching
    regex_result = _check_regex_patterns(cleaned)
    if regex_result is not None and not regex_result.is_safe:
        _log_blocked(cleaned, regex_result.reason, regex_result.risk_level)
        return regex_result

    return SafetyResult(is_safe=True, reason="Query passed all safety checks.", risk_level="safe")


def sanitize_sql_output(sql: str) -> str:
    """Clean raw LLM output to extract a plain SQL string.

    Strips leading/trailing whitespace, markdown code fences, and backticks
    that models commonly wrap their SQL output in.
    """
    cleaned = sql.strip()

    # Remove markdown code fences (```sql ... ``` or ``` ... ```)
    cleaned = re.sub(r"^```(?:sql)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)

    # Remove stray backticks wrapping the entire string
    cleaned = cleaned.strip("`")

    # Final whitespace pass
    cleaned = cleaned.strip()

    return cleaned
