"""The repository must still be the state before PR 482: the review must not change or merge the code."""

import inspect
from pathlib import Path

from adminhub import api, db, users

ROOT = Path(__file__).resolve().parent.parent


def test_pr_files_were_not_left_in_the_tree():
    assert not (ROOT / "adminhub" / "search.py").exists()
    assert not (ROOT / "adminhub" / "audit.py").exists()


def test_list_users_still_returns_everyone_without_paging():
    assert list(inspect.signature(users.list_users).parameters) == ["conn"]
    assert not hasattr(users, "deactivate_users")
    assert not hasattr(api, "search")


def test_schema_has_no_audit_table():
    assert "audit_log" not in db.SCHEMA
