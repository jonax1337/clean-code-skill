import pytest

from hidden_support import RecordingGateway, RecordingNotifier, customer, make_coupons, make_inventory, make_order
from shop.checkout import process_order
from shop.models import Item


def total_for(order, buyer, coupons=None) -> int:
    process_order(order, buyer, make_inventory(), RecordingGateway(), RecordingNotifier(), coupons or make_coupons())
    return order.total_cents


def test_tax_is_rounded_half_up_per_line():
    # Lines of 150, 250 and 350 cents at 19%: 28.5, 47.5 and 66.5 round to 29, 48 and 67.
    order = make_order(Item("pen", 1, 150), Item("ink", 1, 250), Item("pad", 1, 350))
    assert total_for(order, customer()) == 750 + (29 + 48 + 67) + 490


def test_tax_is_charged_on_the_undiscounted_lines():
    order = make_order(Item("pen", 1, 1000), coupon="SPRING10")
    assert total_for(order, customer()) == 1000 - 100 + 190 + 490


def test_discounts_are_rounded_down_to_whole_cents():
    order = make_order(Item("pen", 1, 999), coupon="SPRING10")
    assert total_for(order, customer()) == 999 - 99 + 190 + 490


def test_vip_discount_applies_to_the_amount_left_after_the_coupon():
    order = make_order(Item("pen", 10, 1000), coupon="SPRING10")
    # 10000 - 1000 (coupon) - 450 (5% of the remaining 9000) = 8550, which ships for free
    assert total_for(order, customer(vip=True)) == 8550 + 1900


def test_vip_discount_without_a_coupon():
    order = make_order(Item("pen", 1, 1999))
    assert total_for(order, customer(vip=True)) == 1999 - 99 + 380 + 490


@pytest.mark.parametrize(
    ("unit_price", "expected"),
    [(4999, 4999 + 405 + 490), (5000, 5000 + 405)],
)
def test_shipping_is_free_from_exactly_five_thousand_cents(unit_price, expected):
    assert total_for(make_order(Item("pen", 1, unit_price)), customer(country="CH")) == expected


def test_shipping_threshold_is_checked_after_the_discount():
    order = make_order(Item("pen", 1, 5000), coupon="SPRING10")
    assert total_for(order, customer(country="CH")) == 4500 + 405 + 490


def test_unknown_countries_pay_the_default_tax_rate():
    assert total_for(make_order(Item("pen", 1, 1000)), customer(country="US")) == 1000 + 210 + 490
