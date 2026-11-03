from decimal import Decimal

TAX_RATES = {
    "DE": Decimal("0.19"),
    "FR": Decimal("0.20"),
    "CH": Decimal("0.081"),
}
DEFAULT_TAX_RATE = Decimal("0.21")


def tax_rate(country: str) -> Decimal:
    return TAX_RATES.get(country, DEFAULT_TAX_RATE)
