I've split `process_order` into small helper functions, and all 22 tests pass before and after the change.

**Making sure behavior didn't change:** the existing tests didn't cover enough of the function to prove that, so first I added `tests/test_checkout_characterization.py` with 13 new tests and ran them against the **original** code, where they all passed. They lock in:
- the exact totals for VIP discounts, a coupon combined with VIP, free shipping at exactly 5000 cents, the shipping threshold being checked after discounts, tax rounded per line, and the default tax rate for unknown countries
- that a bad quantity or bad coupon is rejected before any stock is reserved, and the order status stays `"new"`
- the exact order of reserve, release and commit calls when stock runs out partway, when a payment is declined, and when the order succeeds
- that the coupon is only used up when the order succeeds
- that a failed receipt is only logged as a warning, and the order still goes through
- the error messages and their underlying causes

**The refactor** (`shop/checkout.py`): `process_order` is now six readable steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)   # → _subtotal_and_tax, _discount, _shipping
reserved = _reserve_stock(order, inventory)      # rolls back on OutOfStock
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)  # releases stock on decline
_complete_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
```

The logic inside each step is the same code as before, just moved, and everything still runs in the same order. That includes the coupon still being checked during pricing, before any stock is reserved. The two copies of the stock-release loop are now one function, `_release`. The function's signature, error messages, log messages and status values are unchanged, so `shop/api.py` and other callers aren't affected.

I haven't committed anything. Both changes are in your working tree for you to review.