import sqlite3
from datetime import datetime

DB_PATH = "api_error.db"


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS apiDetails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request TEXT,
    response TEXT,
    createdOn Date,
    field1 TEXT,
    field2 TEXT,
    field3 TEXT
)
"""

INSERT_SQL = """
INSERT INTO apiDetails (request, response, createdOn, field1, field2, field3)
VALUES (?, ?, ?, ?, ?, ?)
"""

GET_ALL_SQL = "SELECT id, request, response, createdOn, field1, field2, field3 FROM apiDetails ORDER BY id DESC"
DELETE_SQL = "DELETE FROM apiDetails WHERE id = ?"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as con:
        con.execute(SCHEMA_SQL)


def get_all_data() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute(GET_ALL_SQL).fetchall()
    return rows


def add_and_check_error(payload: str) -> None:
    created_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            INSERT_SQL,
            (payload, "", created_on, "", "", ""),
        )


def delete_data(id_to_delete: int) -> bool:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(DELETE_SQL, (id_to_delete,))
        return cur.rowcount > 0
