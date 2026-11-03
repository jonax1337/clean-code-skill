import pytest

from shop.checkout import process_order, refund_order
from shop.errors import OrderRejected
from shop.models import Customer, Item, Order
from tests.conftest import FakeGateway

CUSTOMER = Customer(email="ada@example.com")


def make_order(*items: Item, coupon: str | None = None) -> Order:
    return Order(id=7, items=list(items), coupon=coupon)


def test_paid_order_charges_price_tax_and_shipping(inventory, gateway, notifier, coupons):
    order = make_order(Item("pen", 2, 1000))

    receipt_id = process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)

    # 2000 + 19% tax (380) + 490 shipping
    assert gateway.charges == [("ada@example.com", 2870)]
    assert (order.status, order.total_cents, receipt_id) == ("paid", 2870, "rcpt-1")
    assert notifier.sent == [("ada@example.com", 7, "rcpt-1")]
    assert inventory.available("pen") == 8


def test_coupon_discount_is_applied_and_redeemed(inventory, gateway, notifier, coupons):
    order = make_order(Item("pen", 4, 1000), coupon="SPRING10")

    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)

    # 4000 - 10% = 3600, + 760 tax, shipping is not free below 5000
    assert order.total_cents == 3600 + 760 + 490
    coupons.redeem("SPRING10")
    assert coupons.discount_percent("SPRING10") is None


def test_order_without_items_is_rejected(inventory, gateway, notifier, coupons):
    with pytest.raises(OrderRejected, match="no items"):
        process_order(make_order(), CUSTOMER, inventory, gateway, notifier, coupons)


def test_out_of_stock_rejects_the_order(inventory, gateway, notifier, coupons):
    order = make_order(Item("ink", 4, 500))

    with pytest.raises(OrderRejected, match="out of stock: ink"):
        process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)

    assert order.status == "rejected"
    assert gateway.charges == []


def test_declined_payment_gives_the_stock_back(inventory, notifier, coupons):
    order = make_order(Item("pen", 3, 1000))

    with pytest.raises(OrderRejected, match="payment declined"):
        process_order(order, CUSTOMER, inventory, FakeGateway(decline=True), notifier, coupons)

    assert order.status == "payment_failed"
    assert inventory.available("pen") == 10
    assert notifier.sent == []


def test_refund_puts_the_items_back(inventory, gateway, notifier, coupons):
    order = make_order(Item("pen", 2, 1000))
    process_order(order, CUSTOMER, inventory, gateway, notifier, coupons)

    refund_order(order, CUSTOMER, inventory, gateway)

    assert gateway.refunds == [("ada@example.com", 2870)]
    assert order.status == "refunded"
    assert inventory.available("pen") == 10


def test_unpaid_order_cannot_be_refunded(inventory, gateway):
    with pytest.raises(OrderRejected, match="not paid"):
        refund_order(make_order(Item("pen", 1, 100)), CUSTOMER, inventory, gateway)
