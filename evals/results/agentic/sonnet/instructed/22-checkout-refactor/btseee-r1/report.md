I split `process_order` in `shop/checkout.py` into small private helpers. The 9 existing tests pass before and after. They don't cover everything, so the behaviour-preserving claim rests partly on a manual check described below.

`process_order` now reads as a sequence of steps:

```python
_validate_items(order)
total = _price_order(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete_order(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

- **Pricing:** `_price_order` handles the total. `_subtotal_and_tax` and `_discount` sit under it, and the per-line tax comment moved with the tax code.
- **Reserve and charge:** `_reserve_stock` and `_charge` each keep their own rollback and status change. They now share a small `_release` helper for the duplicated release loop.
- **Completion and receipt:** `_complete_order` commits stock, redeems the coupon, sets the status and logs. `_send_receipt` keeps the "log a warning and carry on" behaviour.

**Behaviour:** The order of side effects is unchanged. The coupon check still happens before any stock is reserved. Messages, statuses, exception chaining and the rounding and discount arithmetic are all copied as they were. `refund_order` is untouched. The only other change is importing `Item` for a type hint.

**Not covered by tests:** The existing tests don't cover VIP discounts, free shipping, an invalid coupon, a bad quantity, or a receipt that fails to send. I compared those paths against the old code by reading, not by running them. If you want extra safety for production, I can add tests for those cases first.

I haven't committed anything.