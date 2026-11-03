I split `process_order` into small helpers in `shop/checkout.py`. Behavior is unchanged, and the existing tests pass (9/9).

The new `process_order` reads as a short sequence of steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, total, inventory, reserved)
_mark_paid(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

The helpers are `_validate_items`, `_order_total`, `_subtotal_and_tax`, `_discount_cents`, `_shipping_cents`, `_reserve_stock`, `_charge`, `_mark_paid`, `_send_receipt` and `_release`. `refund_order` and the public signature are untouched.

To check that behavior really is unchanged, I ran the original and refactored functions against 20,000 randomized scenarios. The scenarios covered empty or invalid items, bad coupons, VIP and non-VIP customers, several countries, out-of-stock, declined payments, gateway exceptions and receipt failures. Return values, exceptions (including causes), order status and totals, gateway and notifier calls, and inventory and coupon state all matched in every case. The original is still in `git show HEAD:shop/checkout.py`, and the comparison script is in `C:\Users\Jonas\AppData\Local\Temp\difftest` outside the repo.

Two details I kept deliberately:
- Stock is released only on `OutOfStock` and `PaymentDeclined`. Any other exception still propagates without a release, as before.
- The receipt is still sent after the order is marked paid, and receipt failures are still logged and swallowed.

The change is uncommitted in the working tree. I didn't commit or push, since you didn't ask for that.