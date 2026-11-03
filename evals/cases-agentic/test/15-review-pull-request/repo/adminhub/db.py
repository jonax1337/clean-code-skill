"""SQLite access for the admin service."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
"""


def connect(path: str = "adminhub.db") -> sqlite3.Connection:
    """Open the database, creating the tables on first use."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
