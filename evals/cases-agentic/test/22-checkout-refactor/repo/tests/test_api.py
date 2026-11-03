from shop.api import handle_checkout


def payload(quantity: int = 1) -> dict:
    return {
        "order_id": 3,
        "customer": {"email": "bob@example.com", "country": "FR"},
        "items": [{"sku": "pen", "quantity": quantity, "unit_price_cents": 1000}],
    }


def test_successful_checkout_is_described(inventory, gateway, notifier, coupons):
    result = handle_checkout(payload(), inventory, gateway, notifier, coupons)

    assert result == {"ok": True, "status": "paid", "total_cents": 1000 + 200 + 490, "receipt_id": "rcpt-1"}


def test_rejected_checkout_reports_the_reason(inventory, gateway, notifier, coupons):
    result = handle_checkout(payload(quantity=99), inventory, gateway, notifier, coupons)

    assert result == {"ok": False, "status": "rejected", "error": "out of stock: pen"}
