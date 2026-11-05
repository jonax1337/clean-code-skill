I split `process_order` in `shop/checkout.py` into small private helpers, and behavior is unchanged as far as the tests can show. All 20 tests pass, and I haven't committed anything.

`process_order` is now a short sequence that reads as the checkout flow:

```python
_validate_items(order)
total = _total_cents(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, reserved, inventory, gateway)
_complete(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

- **Pricing:** `_total_cents` is built from `_subtotal_and_tax` and `_discount_cents`.
- **Stock:** `_reserve_stock` rolls back a partial reservation on `OutOfStock`, using a shared `_release` helper.
- **Payment:** `_charge` releases the stock if the payment is declined.
- **Completion:** `_complete` commits stock, redeems the coupon, and sets the order to paid.
- **Receipt:** `_send_receipt` still logs a failure and carries on.

I kept the order of checks and side effects the same:
- `tax_rate` is looked up before the coupon check.
- A bad coupon is rejected before any stock is reserved.
- The coupon is only redeemed after the charge succeeds.
- Statuses, error messages, exception chaining and log lines are the same.
- The per-line tax rounding and its comment are intact.

The existing tests didn't cover most of this logic. Before refactoring I added 11 tests to `tests/test_checkout.py` and confirmed they passed against the original code:
- VIP discount stacked on a coupon
- the free-shipping boundary at exactly 5000
- per-line tax rounding
- country tax rates
- invalid quantity
- an unknown coupon
- releasing a partial reservation
- no coupon redemption when the payment is declined
- a failing notifier not undoing a paid order

I got one expected value wrong in the new tests. The code was right, so I fixed the test.

- **Not covered:** the real `Inventory`, `CouponBook` and gateway were only run through the test fakes, and I didn't check `shop/api.py`. The public signature and return value of `process_order` are unchanged.
- **Not changed:** `order.status` stays `"new"` when an invalid quantity or coupon rejects the order, but becomes `"rejected"` on out-of-stock. That looks inconsistent, but I preserved it and pinned it in the tests, since changing it would alter production behavior.