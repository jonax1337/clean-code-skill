I've split `process_order` into smaller pieces. It now reads as six steps:

```python
_validate_items(order.items)
total = _calculate_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_finalize_paid_order(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

The pricing step is split again into `_subtotal_and_tax` and `_discount`, and both rollback paths share a `_release` helper. The function's signature, return value, error messages, status changes, log messages and the order of calls to inventory, the payment gateway and the coupons are all the same as before. `shop/api.py` calls it unchanged.

**How I checked behavior didn't change:** the existing tests skipped many paths, so before touching the code I wrote 10 more tests in `tests/test_checkout_behavior.py` and ran them against the original version. All passed. They cover:
- tax rounded per line, using the customer's country and the price before discounts
- the coupon and VIP discounts stacking, and where the free-shipping cutoff falls
- bad quantities and used-up coupons being rejected before any stock is reserved
- when an item is out of stock, only the items already reserved being released (checked against the exact inventory log)
- a declined payment releasing all stock and not using up the coupon
- a failed receipt email being logged while the order stays paid

After the refactor, all 19 tests (the 9 old ones plus the 10 new ones) still pass.

**One thing to review:** when a payment is declined, the new code releases `order.items` instead of a separate `reserved` list. By that point every item has been reserved, so the two lists hold the same items in the same order, and a test checks that the release calls match exactly.

I haven't committed anything. The changes are in `shop/checkout.py` and the new test file, ready for you to review.