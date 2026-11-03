from decimal import Decimal

from shop.money import format_eur, round_cents


def test_rounds_half_up():
    assert round_cents(Decimal("2.345")) == Decimal("2.35")


def test_formats_with_german_separators():
    assert format_eur(Decimal("1234.5")) == "1.234,50 EUR"


def test_formats_small_amounts():
    assert format_eur(Decimal("0.07")) == "0,07 EUR"
