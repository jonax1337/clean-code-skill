I split `process_order` in `shop/checkout.py` into small private helpers. All 9 existing tests pass, and I ran them before and after. I haven't committed anything.

`process_order` now reads as the sequence of steps:

```python
_validate_items(order)
total = _order_total_cents(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_complete_order(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

- **Pricing:** `_order_total_cents` combines `_subtotal_and_tax_cents` and `_discount_cents` with the shipping rule. The comment about per-line tax rounding stayed with the code it explains.
- **Stock and payment:** `_reserve_stock`, `_charge` and `_release_stock` hold the rollback logic. The release loop was duplicated in two places, and now it exists once.
- **After payment:** `_complete_order` commits stock, redeems the coupon, sets the status and logs. `_send_receipt` still only logs a warning if the email fails.

Behavior should be identical:
- The order of side effects is unchanged. The tax rate lookup comes before coupon validation, and coupon validation comes before any stock is reserved. The coupon is redeemed only after the charge succeeds.
- The exceptions, their messages and `from error` chaining, and the status values (`rejected`, `payment_failed`, `paid`) are the same.
- No public signatures changed, and `refund_order` is untouched.

The tests only cover 9 cases, so I can't promise every path is exercised. I haven't checked which paths they hit, such as VIP together with a coupon, or the out-of-stock rollback. If you want more confidence before deploying, I can add tests for those.