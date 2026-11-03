I split `process_order` in `shop/checkout.py` into small private helpers. The 9 existing tests pass. I haven't committed anything.

`process_order` now reads as the sequence of steps it performs:

```python
_validate_items(order)
total = _calculate_total(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_finalize_paid_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

The pricing logic is split further into `_subtotal_and_tax` and `_discount`.

**Behavior I kept the same**
- **Step order:** Tax is still computed before the coupon is checked. An unknown country therefore still fails before an invalid coupon does.
- **Stock release:** Reserved items are released only on `OutOfStock` or `PaymentDeclined`, as before. Any other exception still releases nothing.
- **Status changes:** Each failure sets the same `order.status` value as before. The exception messages are unchanged.
- **Receipt failures:** A failure sending the receipt is still logged and swallowed.
- **Signature:** `process_order`'s public signature is unchanged, so `api.py` and other callers need no changes.
- **Duplicate code:** The release loop that appeared twice is now one helper, `_release_all` (G5).

**Left alone:** `process_order` still takes 6 arguments, more than the F1 limit of 3. Fixing that would change its public signature, so I held off given it's live in production. Grouping the dependencies into one object would be a separate change.

The tests only cover 9 cases. If you want more safety before deploying, I can add tests for the edge cases above: unknown country with a bad coupon, a VIP discount combined with a coupon, free-shipping thresholds, and a failed receipt send.