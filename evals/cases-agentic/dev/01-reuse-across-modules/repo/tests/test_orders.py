from decimal import Decimal

from shop.orders import LineItem, Order, gross_total, vat_total


def test_vat_is_rounded_per_line():
    order = Order("A-1", "Max", "max@example.com", [LineItem("P", "Pen", Decimal("0.05"), 1)] * 3)
    assert vat_total(order) == Decimal("0.03")


def test_gross_total_includes_shipping():
    order = Order("A-2", "Max", "max@example.com", [LineItem("B", "Book", Decimal("10.00"), 1, "reduced")])
    order.shipping = Decimal("4.90")
    assert gross_total(order) == Decimal("15.60")
