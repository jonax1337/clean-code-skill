import logging

from hidden_support import RecordingGateway, RecordingNotifier, customer, make_coupons, make_inventory, make_order
from shop.checkout import process_order
from shop.models import Item

PAID_TOTAL = 2500 - 250 + 475 + 490  # subtotal, 10% coupon, tax per line (380 + 95), shipping


def paid_order():
    return make_order(Item("pen", 2, 1000), Item("pad", 1, 500), coupon="SPRING10")


def test_stock_is_reserved_before_the_charge_and_committed_after_it():
    inventory = make_inventory()
    gateway = RecordingGateway(inventory)

    receipt_id = process_order(paid_order(), customer(), inventory, gateway, RecordingNotifier(), make_coupons())

    assert gateway.inventory_log_at_charge == [("reserve", "pen", 2), ("reserve", "pad", 1)]
    assert inventory.log == [
        ("reserve", "pen", 2),
        ("reserve", "pad", 1),
        ("commit", "pen", 2),
        ("commit", "pad", 1),
    ]
    assert gateway.charges == [("ada@example.com", PAID_TOTAL)]
    assert receipt_id == "rcpt-1"


def test_the_coupon_is_redeemed_once_and_only_after_payment():
    coupons = make_coupons(uses=1)
    process_order(paid_order(), customer(), make_inventory(), RecordingGateway(), RecordingNotifier(), coupons)
    assert coupons.discount_percent("SPRING10") is None


def test_the_order_is_marked_paid_and_the_receipt_is_sent():
    notifier = RecordingNotifier()
    order = paid_order()
    receipt_id = process_order(order, customer(), make_inventory(), RecordingGateway(), notifier, make_coupons())
    assert order.status == "paid"
    assert order.total_cents == PAID_TOTAL
    assert notifier.sent == [("ada@example.com", 7, receipt_id)]


def test_a_failing_notifier_does_not_fail_the_order_but_is_logged(caplog):
    order = paid_order()
    notifier = RecordingNotifier(fail=True)
    with caplog.at_level(logging.INFO, logger="shop.checkout"):
        receipt_id = process_order(order, customer(), make_inventory(), RecordingGateway(), notifier, make_coupons())

    assert (receipt_id, order.status) == ("rcpt-1", "paid")
    warnings = [record for record in caplog.records if record.levelno == logging.WARNING]
    assert [record.getMessage() for record in warnings] == ["receipt for order 7 could not be sent"]
    assert warnings[0].exc_info is not None
    assert warnings[0].name == "shop.checkout"


def test_a_paid_order_is_logged_at_info_level(caplog):
    with caplog.at_level(logging.INFO, logger="shop.checkout"):
        process_order(paid_order(), customer(), make_inventory(), RecordingGateway(), RecordingNotifier(), make_coupons())
    infos = [record for record in caplog.records if record.levelno == logging.INFO]
    assert [(record.name, record.getMessage()) for record in infos] == [("shop.checkout", f"order 7 paid: {PAID_TOTAL} cents")]


def test_the_items_of_the_order_are_left_alone():
    order = paid_order()
    before = [(item.sku, item.quantity, item.unit_price_cents) for item in order.items]
    process_order(order, customer(), make_inventory(), RecordingGateway(), RecordingNotifier(), make_coupons())
    assert [(item.sku, item.quantity, item.unit_price_cents) for item in order.items] == before
