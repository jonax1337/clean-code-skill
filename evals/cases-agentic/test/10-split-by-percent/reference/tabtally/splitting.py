"""Decide how much of an expense each person owes."""

from tabtally.errors import MoneyError
from tabtally.money import allocate


def split_equally(cents: int, people: list[str]) -> dict[str, int]:
    duplicates = sorted({name for name in people if people.count(name) > 1})
    if duplicates:
        raise MoneyError(f"listed more than once: {', '.join(duplicates)}")
    return dict(zip(people, allocate(cents, [1] * len(people))))


def split_by_percent(cents: int, percents: dict[str, int]) -> dict[str, int]:
    total = sum(percents.values())
    if total != 100:
        raise MoneyError(f"percentages add up to {total}, not 100")
    return dict(zip(percents, allocate(cents, list(percents.values()))))
