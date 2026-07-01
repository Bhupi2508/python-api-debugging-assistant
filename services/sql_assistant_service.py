"""SQL Assistant service.

This service is responsible for:
- Interpreting natural language via an LLM
- Generating a *single* safe SELECT SQL query
- Executing it against the local SQLite DB
- Returning *only* database results (no invented answers)

Important security constraints:
- Allow only SELECT statements
- Block dangerous keywords
- Prevent multiple statements
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Any

import database
from services.ai_manager import complete

FORBIDDEN_KEYWORDS = {
    # destructive / schema changing
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "truncate",
    "create",
    "replace",
    # attachment / temp changes
    "attach",
    "detach",
    # transaction controls
    "begin",
    "commit",
    "rollback",
    # sqlite-specific meta operations
    "pragma",
    "vacuum",
}


@dataclass(frozen=True)
class SQLValidationResult:
    ok: bool
    error: str | None = None


def _get_db_schema_for_llm() -> str:
    """Return a minimal schema description for the LLM."""
    # The only table we control is developer_queries.
    # We provide a compact schema plus guidance on where relevant data lives.
    schema_sql = database.SCHEMA_SQL.strip()
    guidance = (
        "\n\nGuidance for queries:\n"
        "- Use table developer_queries (id, action_type, query, created_on, ai_response, ai_provider, model).\n"
        "- 'query' holds the original user input for the feature execution.\n"
        "- For 'Explain Error' / SQL Assistant history, look for error keywords inside developer_queries.query or developer_queries.ai_response depending on your intent.\n"
        "- 'created_on' is stored as 'YYYY-MM-DD HH:MM:SS'.\n"
    )
    return schema_sql + guidance


def _validate_sql(sql: str) -> SQLValidationResult:
    raw = (sql or "").strip()
    if not raw:
        return SQLValidationResult(ok=False, error="Model returned empty SQL.")

    # Disallow multiple statements.
    # Allow a single trailing semicolon (common in model outputs).
    stripped = raw.rstrip()
    if ";" in stripped[:-1]:
        return SQLValidationResult(
            ok=False, error="SQL must be a single statement (no multiple statements)."
        )
    if stripped.endswith(";"):
        raw = stripped[:-1].strip()

    # SELECT-only
    if not re.match(r"(?is)^\s*select\b", raw):
        return SQLValidationResult(ok=False, error="Only SELECT queries are allowed.")

    lower = raw.lower()
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return SQLValidationResult(
                ok=False, error=f"Forbidden keyword detected: {kw}"
            )

    return SQLValidationResult(ok=True)


def _rows_to_text(rows: list[tuple[Any, ...]], cursor_description: Any) -> str:
    if not rows:
        return "No matching records were found for your request."

    # Column names from cursor description
    columns = [col[0] for col in cursor_description]

    # Limit rows to keep CLI output reasonable.
    max_rows = 50
    limited = rows[:max_rows]

    # Build simple text table.
    col_widths = [len(str(c)) for c in columns]
    for r in limited:
        for i, v in enumerate(r):
            col_widths[i] = max(col_widths[i], len(str(v)))

    def fmt_row(r: tuple[Any, ...]) -> str:
        parts = []
        for i, v in enumerate(r):
            s = "NULL" if v is None else str(v)
            parts.append(s.ljust(col_widths[i]))
        return " | ".join(parts)

    header = " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns))
    sep = "-+-".join("-" * w for w in col_widths)

    body_lines = [fmt_row(r) for r in limited]
    tail = ""
    if len(rows) > max_rows:
        tail = f"\n… (showing first {max_rows} of {len(rows)} rows)"

    return header + "\n" + sep + "\n" + "\n".join(body_lines) + tail


def sql_assistant_service(user_input: str) -> str:
    """Natural language -> SQL -> execute -> return results."""

    input_text = (user_input or "").strip()
    if not input_text:
        raise ValueError("SQL input cannot be empty.")

    # Load prompt template
    from pathlib import Path

    PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
    template = (PROMPTS_DIR / "sql_assistant.txt").read_text(encoding="utf-8")

    schema = _get_db_schema_for_llm()
    prompt = template.format(input=input_text, schema=schema)

    # Ask the model for SQL.
    model_output = complete(prompt)
    # The model is instructed to output ONLY SQL, but we defensively try to extract SQL.
    # Strip code fences if present.
    cleaned = (model_output or "").strip()
    cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    sql = cleaned.strip()

    validation = _validate_sql(sql)
    if not validation.ok:
        return f"SQL validation failed: {validation.error}"

    # Execute SQL.
    try:
        conn = database._get_connection()  # reuse existing connection
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        return _rows_to_text(rows, cursor.description)
    except sqlite3.Error as exc:
        return f"SQL execution failed: {exc}"
