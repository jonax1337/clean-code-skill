"""Decide how much of an expense each person owes."""

from tabtally.errors import MoneyError
from tabtally.money import allocate


def split_equally(cents: int, people: list[str]) -> dict[str, int]:
    duplicates = sorted({name for name in people if people.count(name) > 1})
    if duplicates:
        raise MoneyError(f"listed more than once: {', '.join(duplicates)}")
    return dict(zip(people, allocate(cents, [1] * len(people))))
