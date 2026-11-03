I split `process_order` into small helpers, and behavior is unchanged. All 24 tests pass, including 15 new ones.

**What it looks like now** (`shop/checkout.py`): the function is a short list of steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_complete_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

The pricing logic is split further into `_subtotal_and_tax` and `_discount`. A small `_release` helper replaces the two copies of the stock-release loop. Each step does exactly what the old code did, in the same order. That includes when `order.status` is set, rejecting an invalid coupon before any stock is reserved, and chaining exceptions with `from error`. The public signature didn't change, so `shop/api.py` needed no edits.

**How I checked it:** the existing tests didn't cover a lot of the risky logic. So before changing any code, I added `tests/test_checkout_characterization.py` and made sure it passed against the original code. It covers:
- VIP discount on its own and stacked after a coupon
- the free-shipping threshold, which uses the discounted subtotal
- tax rounded per line, half-up, plus the default tax rate for unknown countries
- quantities of zero or less, and invalid or used-up coupons, rejected without touching stock
- an out-of-stock item releasing only what was already reserved, and leaving the coupon unredeemed
- a declined payment releasing all stock and leaving the coupon and total unchanged
- the exact order of reserve and commit calls on success
- a failed receipt send being logged without failing the order

I haven't committed anything. The changes are in your working tree for you to review.