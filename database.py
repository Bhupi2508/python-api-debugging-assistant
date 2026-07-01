"""SQLite database layer for storing developer queries."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_DIR = Path(__file__).resolve().parent / "database"
DB_PATH = DB_DIR / "developer_history.db"
EXPORTS_DIR = Path(__file__).resolve().parent / "exports"

TABLE_NAME = "developer_queries"
MAX_QUERY_LENGTH = 100_000

ACTION_LABELS: dict[str, str] = {
    "explain_error": "Explain an Error",
    "explain_code": "Explain Code",
    "improve_code": "Improve Code",
    "generate_tests": "Generate Unit Tests",
    "sql_assistant": "SQL Assistant",
    "regex_generator": "Regex Generator",
    "git_assistant": "Git Assistant",
    "general": "General Query",
}

SCHEMA_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL DEFAULT 'general',
    query TEXT NOT NULL,
    created_on TEXT NOT NULL,

    -- Phase 2 AI fields (kept minimal for beginner readability)
    ai_response TEXT,
    ai_provider TEXT,
    model TEXT
)
"""


INSERT_SQL = (
    f"INSERT INTO {TABLE_NAME} (action_type, query, created_on) VALUES (?, ?, ?)"
)
GET_ALL_SQL = (
    f"SELECT id, action_type, query, created_on, ai_response, ai_provider, model "
    f"FROM {TABLE_NAME} ORDER BY id DESC"
)


DELETE_BY_ID_SQL = f"DELETE FROM {TABLE_NAME} WHERE id = ?"
DELETE_ALL_SQL = f"DELETE FROM {TABLE_NAME}"
COUNT_BY_ID_SQL = f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE id = ?"

_connection: sqlite3.Connection | None = None


def _get_connection() -> sqlite3.Connection:
    """Return a reusable SQLite connection."""
    global _connection
    if _connection is None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH)
    return _connection


def _format_timestamp(dt: datetime | None = None) -> str:
    """Return a readable timestamp string for database storage."""
    moment = dt or datetime.now()
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def _ensure_action_type_column(connection: sqlite3.Connection) -> None:
    """Add action_type column to older databases if missing."""
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({TABLE_NAME})")}
    if "action_type" not in columns:
        connection.execute(
            f"ALTER TABLE {TABLE_NAME} "
            f"ADD COLUMN action_type TEXT NOT NULL DEFAULT 'general'"
        )


def _ensure_ai_columns(connection: sqlite3.Connection) -> None:
    """Ensure Phase 2 AI response columns exist for older DB files."""
    columns = {row[1] for row in connection.execute(f"PRAGMA table_info({TABLE_NAME})")}

    if "ai_response" not in columns:
        connection.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN ai_response TEXT")
    if "ai_provider" not in columns:
        connection.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN ai_provider TEXT")
    if "model" not in columns:
        connection.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN model TEXT")


def initialize_database() -> None:
    """Create database tables if they do not exist."""
    connection = _get_connection()
    connection.execute(SCHEMA_SQL)
    _ensure_action_type_column(connection)
    _ensure_ai_columns(connection)
    connection.commit()


def save_query(query: str, action_type: str = "general") -> int:
    """Save a developer query and return the new record ID."""
    connection = _get_connection()
    cursor = connection.execute(
        INSERT_SQL,
        (action_type, query, _format_timestamp()),
    )
    connection.commit()
    return int(cursor.lastrowid)


def get_all_queries() -> list[tuple[Any, ...]]:
    """Return all saved queries/records, newest first."""
    connection = _get_connection()
    return connection.execute(GET_ALL_SQL).fetchall()


def save_ai_response(
    record_id: int,
    ai_response: str,
    ai_provider: str | None,
    model: str | None,
) -> None:
    """Store AI response for an existing record."""

    connection = _get_connection()
    connection.execute(
        f"UPDATE {TABLE_NAME} SET ai_response = ?, ai_provider = ?, model = ? WHERE id = ?",
        (ai_response, ai_provider, model, record_id),
    )
    connection.commit()


def delete_query(record_id: int) -> bool:
    """Delete a single query by ID. Returns True if a row was removed."""
    connection = _get_connection()
    cursor = connection.execute(DELETE_BY_ID_SQL, (record_id,))
    connection.commit()
    return cursor.rowcount > 0


def delete_all_queries() -> int:
    """Delete all queries and return the number removed."""
    connection = _get_connection()
    cursor = connection.execute(DELETE_ALL_SQL)
    connection.commit()
    return cursor.rowcount


def query_exists(record_id: int) -> bool:
    """Return True if a query with the given ID exists."""
    connection = _get_connection()
    count = connection.execute(COUNT_BY_ID_SQL, (record_id,)).fetchone()[0]
    return count > 0


def get_action_label(action_type: str) -> str:
    """Return a human-readable label for an action type."""
    return ACTION_LABELS.get(action_type, action_type.replace("_", " ").title())


def export_session() -> Path:
    """Export all saved queries to a JSON file and return the file path."""
    rows = get_all_queries()

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = EXPORTS_DIR / f"session_{timestamp}.json"

    payload = {
        "exported_on": _format_timestamp(),
        "total_records": len(rows),
        "records": [
            {
                "id": record_id,
                "action_type": action_type,
                "action_label": get_action_label(action_type),
                "query": query,
                "created_on": created_on,
                "ai_response": ai_response,
                "ai_provider": ai_provider,
                "model": model,
            }
            for record_id, action_type, query, created_on, ai_response, ai_provider, model in rows
        ],
    }

    export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return export_path


def close_database() -> None:
    """Close the active database connection."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
