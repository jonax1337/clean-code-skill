I split `process_order` in `shop/checkout.py` into small helpers. All 20 tests pass, including 11 new characterization tests I wrote against the original code before touching it.

The new `process_order` reads as a short sequence:

```python
_validate_order(order)
price = _price_order(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge_customer(order, customer, price.total_cents, inventory, gateway)
_mark_paid(order, price.total_cents, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

Pricing is now a small `_Price` dataclass with a `total_cents` property. Subtotal, tax, coupon/VIP discount and shipping each have their own helper. The per-line tax rounding is unchanged and its comment moved to `_tax_cents`.

Behavior is unchanged in the places that matter for production:
- Validation, pricing and coupon checks run before any stock is reserved, in the same order as before.
- Stock is released on out-of-stock (only the items reserved so far) and on a payment decline (all items).
- Exceptions other than `OutOfStock` and `PaymentDeclined` still propagate without any release, and a failing receipt is still logged and swallowed.

**Files changed:**
- `shop/checkout.py`: the refactor. `refund_order` is untouched.
- `tests/test_checkout_behavior.py` (new): the characterization tests. Keep these, since the existing suite did not cover the VIP discount, free-shipping threshold, partial-reservation rollback, receipt failure or unexpected gateway errors.

I did not commit anything.

**Found but not changed:** if `gateway.charge` raises something other than `PaymentDeclined` (for example a timeout), the reserved stock is never released, and the order stays in status `"new"`. The test `test_unexpected_gateway_error_propagates_without_release` pins this current behavior. That is a likely real bug, but fixing it would change production behavior, so I left it for you to decide.