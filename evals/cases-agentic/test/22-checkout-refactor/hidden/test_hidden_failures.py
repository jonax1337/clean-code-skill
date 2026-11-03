import pytest

from hidden_support import RecordingGateway, RecordingNotifier, customer, make_coupons, make_inventory, make_order
from shop.checkout import process_order
from shop.errors import OrderRejected, PaymentDeclined
from shop.models import Item


def reject(order, inventory=None, gateway=None, notifier=None, coupons=None):
    """Runs the checkout, expects a rejection and returns it with the collaborators that were used."""
    inventory = inventory or make_inventory()
    gateway = gateway or RecordingGateway(inventory)
    notifier = notifier or RecordingNotifier()
    coupons = coupons or make_coupons()
    with pytest.raises(OrderRejected) as rejection:
        process_order(order, customer(), inventory, gateway, notifier, coupons)
    return rejection.value, inventory, gateway, notifier


def test_empty_order_is_rejected_before_anything_happens():
    error, inventory, gateway, _ = reject(make_order())
    assert str(error) == "order has no items"
    assert inventory.log == [] and gateway.charges == []


def test_a_bad_quantity_anywhere_in_the_order_is_rejected_before_any_stock_is_reserved():
    order = make_order(Item("pen", 1, 100), Item("ink", 0, 100))
    error, inventory, _, _ = reject(order)
    assert str(error) == "invalid quantity for ink"
    assert inventory.log == []
    assert order.status == "new"


@pytest.mark.parametrize("code", ["NOPE", "SPRING10"])
def test_an_invalid_or_used_up_coupon_is_rejected_before_any_stock_is_reserved(code):
    order = make_order(Item("pen", 1, 100), coupon=code)
    error, inventory, _, _ = reject(order, coupons=make_coupons(uses=0))
    assert str(error) == f"invalid coupon: {code}"
    assert inventory.log == []
    assert (order.status, order.total_cents) == ("new", 0)


def test_running_out_of_stock_on_a_later_item_releases_what_was_already_reserved():
    order = make_order(Item("pen", 2, 100), Item("pad", 1, 100), Item("ink", 4, 100))
    error, inventory, gateway, _ = reject(order)
    assert str(error) == "out of stock: ink"
    assert error.__cause__ is not None and error.__cause__.args == ("ink",)
    assert inventory.log == [
        ("reserve", "pen", 2),
        ("reserve", "pad", 1),
        ("release", "pen", 2),
        ("release", "pad", 1),
    ]
    assert gateway.charges == []
    assert (order.status, order.total_cents) == ("rejected", 0)


def test_a_declined_payment_releases_every_reservation_in_order_and_keeps_the_coupon():
    inventory = make_inventory()
    order = make_order(Item("pen", 2, 100), Item("pad", 1, 100), coupon="SPRING10")
    coupons = make_coupons(uses=1)
    error, _, _, notifier = reject(
        order,
        inventory=inventory,
        gateway=RecordingGateway(inventory, decline=True),
        coupons=coupons,
    )
    assert str(error) == "payment declined: card declined"
    assert isinstance(error.__cause__, PaymentDeclined)
    assert inventory.log == [
        ("reserve", "pen", 2),
        ("reserve", "pad", 1),
        ("release", "pen", 2),
        ("release", "pad", 1),
    ]
    assert coupons.discount_percent("SPRING10") == 10
    assert notifier.sent == []
    assert (order.status, order.total_cents) == ("payment_failed", 0)


def test_an_unexpected_gateway_error_is_not_turned_into_a_rejection():
    inventory = make_inventory()
    order = make_order(Item("pen", 1, 100))
    gateway = RecordingGateway(inventory, crash=True)
    with pytest.raises(RuntimeError, match="gateway unreachable"):
        process_order(order, customer(), inventory, gateway, RecordingNotifier(), make_coupons())
    assert (order.status, order.total_cents) == ("new", 0)
