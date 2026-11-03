I've split `process_order` into small helpers. Its signature, behavior and error messages are unchanged. All 18 tests pass on both the original and the refactored code. I haven't committed anything.

**Tests first.** The existing 9 tests missed a lot of the behavior, so before changing any code I added 9 tests to `tests/test_checkout.py` that pin down what the original does today:
- A zero or negative quantity, or an unknown coupon, is rejected before any stock is touched, and the order status stays `"new"`.
- The VIP discount applies to the amount left after the coupon, and tax is charged on the undiscounted price.
- Shipping is free once the discounted subtotal reaches the threshold.
- Tax is rounded per line, not on the sum. One test uses an example where the two give different totals.
- If an item is out of stock, the items already reserved are released.
- A declined payment doesn't use up the coupon.
- A paid order commits the stock and redeems the coupon.
- If the receipt can't be sent, that is logged and the order still succeeds.

**The refactor** (`shop/checkout.py`). `process_order` now reads as the steps of a checkout:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete_payment(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

- Pricing is split into `_line_cents`, `_tax_cents`, `_discount_cents` and `_shipping_cents`.
- Both failure paths (out of stock, declined payment) share one `_release` helper instead of two copies of the same loop.
- The existing comment about per-line tax rounding is kept. I added two short docstrings for rules that aren't obvious from the code: the order the discounts apply in, and why a failed receipt is only logged.
- The order of side effects is the same as before. When a payment is declined, I now release `order.items` instead of the `reserved` list, but at that point the two are always the same.

**Worth knowing:**
- No linter or formatter ran because ruff isn't installed, and the project doesn't configure one.
- My edit script wrote Windows (CRLF) line endings. I converted them back to the repo's LF and checked.
- I left `refund_order` alone since it was outside the task. One thing I noticed there: it refunds `order.total_cents` but never puts back the coupon use. That may be intended, but it's worth a look.