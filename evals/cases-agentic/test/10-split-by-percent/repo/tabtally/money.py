"""Money is a whole number of cents. Never put an amount through a float."""

from decimal import Decimal, InvalidOperation

from tabtally.errors import MoneyError


def parse_amount(text: str) -> int:
    """Turn user input such as "12.50" into cents."""
    try:
        amount = Decimal(text.strip())
    except InvalidOperation:
        raise MoneyError(f"not an amount: {text!r}") from None
    if not amount.is_finite():
        raise MoneyError(f"not an amount: {text!r}")
    cents = amount * 100
    if cents != cents.to_integral_value() or cents <= 0:
        raise MoneyError(f"amount must be positive with at most two decimals: {text!r}")
    return int(cents)


def format_cents(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    whole, part = divmod(abs(cents), 100)
    return f"{sign}{whole}.{part:02d}"


def allocate(cents: int, weights: list[int]) -> list[int]:
    """Split cents in proportion to the weights so that the parts add up to exactly cents.

    Every part is rounded down; the cents left over go to the parts with the largest
    remainders, earlier parts first on a tie.
    """
    total = sum(weights)
    if not weights or total <= 0 or any(weight < 0 for weight in weights):
        raise MoneyError("weights must not be negative and must not all be zero")
    parts = [cents * weight // total for weight in weights]
    by_remainder = sorted(range(len(weights)), key=lambda i: (-(cents * weights[i] % total), i))
    for index in by_remainder[: cents - sum(parts)]:
        parts[index] += 1
    return parts
