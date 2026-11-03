"""Reading and changing users."""

import sqlite3
from datetime import datetime, timezone

from .errors import NotFound
from .models import User

SELECT_USER = "SELECT id, email, name, role, active, created_at FROM users"


def create_user(
    conn: sqlite3.Connection, email: str, name: str, role: str = "member", created_at: str | None = None
) -> User:
    """Insert a user and return it; `created_at` defaults to the current UTC time."""
    created_at = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    cursor = conn.execute(
        "INSERT INTO users (email, name, role, created_at) VALUES (?, ?, ?, ?)",
        (email, name, role, created_at),
    )
    conn.commit()
    return get_user(conn, cursor.lastrowid)


def get_user(conn: sqlite3.Connection, user_id: int) -> User:
    """Return one user or raise NotFound."""
    row = conn.execute(SELECT_USER + " WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise NotFound(f"user {user_id} not found")
    return User.from_row(row)


def list_users(conn: sqlite3.Connection) -> list[User]:
    """All users, ordered by id."""
    rows = conn.execute(SELECT_USER + " ORDER BY id").fetchall()
    return [User.from_row(row) for row in rows]


def deactivate_user(conn: sqlite3.Connection, user_id: int) -> None:
    """Mark a user inactive or raise NotFound."""
    cursor = conn.execute("UPDATE users SET active = 0 WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        raise NotFound(f"user {user_id} not found")
    conn.commit()
