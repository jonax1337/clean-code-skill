"""Money helpers. Amounts are always Decimal, never float."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
_TO_GERMAN_SEPARATORS = str.maketrans({",": ".", ".": ","})


def round_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def format_eur(amount: Decimal) -> str:
    """Format the way German invoices do: 1.234,50 EUR."""
    us_style = f"{round_cents(amount):,.2f}"
    return f"{us_style.translate(_TO_GERMAN_SEPARATORS)} EUR"
