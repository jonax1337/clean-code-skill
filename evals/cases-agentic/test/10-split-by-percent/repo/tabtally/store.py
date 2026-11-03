"""The expense file: JSON with one list of expenses."""

import json
from dataclasses import asdict
from pathlib import Path

from tabtally.errors import StoreError
from tabtally.models import Expense


def load(path: Path) -> list[Expense]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [Expense(**item) for item in raw["expenses"]]
    except (ValueError, KeyError, TypeError) as error:
        raise StoreError(f"cannot read {path}: {error}") from error


def save(path: Path, expenses: list[Expense]) -> None:
    payload = {"expenses": [asdict(expense) for expense in expenses]}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def next_id(expenses: list[Expense]) -> int:
    return max((expense.id for expense in expenses), default=0) + 1
