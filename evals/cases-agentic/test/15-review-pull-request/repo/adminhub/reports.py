"""Aggregated numbers for the dashboard."""

import sqlite3


def signups_per_day(conn: sqlite3.Connection, start: str, end: str) -> list[dict]:
    """Signups per calendar day for `start` <= created_at < `end` (ISO dates)."""
    rows = conn.execute(
        "SELECT date(created_at) AS day, COUNT(*) AS signups FROM users "
        "WHERE created_at >= ? AND created_at < ? GROUP BY day ORDER BY day",
        (start, end),
    ).fetchall()
    return [{"day": row["day"], "signups": row["signups"]} for row in rows]


def active_by_role(conn: sqlite3.Connection) -> dict[str, int]:
    """Number of active users per role."""
    rows = conn.execute("SELECT role, COUNT(*) AS n FROM users WHERE active = 1 GROUP BY role").fetchall()
    return {row["role"]: row["n"] for row in rows}
