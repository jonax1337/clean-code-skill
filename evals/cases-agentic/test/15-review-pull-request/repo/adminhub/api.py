"""Request handlers. Each takes the connection and the decoded request parameters and returns a response dict."""

import sqlite3

from . import reports, users
from .errors import BadRequest, NotFound


def ok(body: dict) -> dict:
    return {"status": 200, "body": body}


def error(status: int, message: str) -> dict:
    return {"status": status, "body": {"error": message}}


def _user_id(params: dict) -> int:
    try:
        return int(params["id"])
    except (KeyError, ValueError):
        raise BadRequest("id must be an integer") from None


def get_user(conn: sqlite3.Connection, params: dict) -> dict:
    try:
        return ok(users.get_user(conn, _user_id(params)).to_dict())
    except NotFound as problem:
        return error(404, str(problem))
    except BadRequest as problem:
        return error(400, str(problem))


def list_users(conn: sqlite3.Connection, params: dict) -> dict:
    return ok({"users": [user.to_dict() for user in users.list_users(conn)]})


def deactivate_user(conn: sqlite3.Connection, params: dict) -> dict:
    try:
        users.deactivate_user(conn, _user_id(params))
    except NotFound as problem:
        return error(404, str(problem))
    except BadRequest as problem:
        return error(400, str(problem))
    return ok({"deactivated": 1})


def signups(conn: sqlite3.Connection, params: dict) -> dict:
    if "start" not in params or "end" not in params:
        return error(400, "start and end are required")
    return ok({"days": reports.signups_per_day(conn, params["start"], params["end"])})
