import pytest

from tabtally.errors import MoneyError
from tabtally.money import allocate, format_cents, parse_amount


@pytest.mark.parametrize(
    ("text", "cents"),
    [("12.50", 1250), ("3", 300), ("0.07", 7), (" 8.5 ", 850)],
)
def test_parse_amount(text, cents):
    assert parse_amount(text) == cents


@pytest.mark.parametrize("text", ["", "abc", "1.234", "0", "-5.00", "nan", "inf"])
def test_parse_amount_rejects_bad_input(text):
    with pytest.raises(MoneyError):
        parse_amount(text)


@pytest.mark.parametrize(
    ("cents", "text"),
    [(1250, "12.50"), (7, "0.07"), (0, "0.00"), (-333, "-3.33")],
)
def test_format_cents(cents, text):
    assert format_cents(cents) == text


def test_allocate_keeps_the_total():
    assert sum(allocate(100, [1, 1, 1])) == 100


def test_allocate_gives_leftover_cents_to_the_largest_remainders():
    assert allocate(10, [1, 1, 1]) == [4, 3, 3]
    assert allocate(10, [3, 3, 4]) == [3, 3, 4]
    assert allocate(7, [2, 1]) == [5, 2]


def test_allocate_rejects_impossible_weights():
    for weights in ([], [0, 0], [-1, 2]):
        with pytest.raises(MoneyError):
            allocate(100, weights)
