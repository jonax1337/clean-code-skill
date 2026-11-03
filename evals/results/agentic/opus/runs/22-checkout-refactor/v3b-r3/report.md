I've split `process_order` into small helpers. Its signature and behavior are the same, and all 21 tests pass on both the old and new code. Nothing is committed yet.

**Tests first.** The existing tests only covered the main paths, so before changing anything I added 12 tests to `tests/test_checkout.py` that record exactly what the current code does:
- **Tax:** rounded half-up per line, not on the sum; charged on the price before discounts; rate set by the customer's country.
- **Discounts:** the VIP discount applies after the coupon discount.
- **Shipping:** free at exactly 50.00, and that limit is checked after discounts.
- **Order of checks:** a bad quantity or coupon is rejected before any stock is reserved, and the order status stays `"new"`.
- **Out of stock:** items already reserved are released, and the coupon is not used up.
- **Declined payment:** stock is released and the coupon is not used up.
- **Stock order:** all items are reserved before any is committed.
- **Receipt failure:** if the receipt email fails, it is logged and the order still counts as paid.

All 21 tests passed against the original code. I then refactored and ran them again: still 21 passed.

**The refactoring.** `process_order` now reads as six steps:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
```

The price is now calculated in four small functions (`_line_cents`, `_tax_cents`, `_discount_cents`, `_shipping_cents`), and the two copies of the stock-release loop became one `_release_stock`. I kept the existing comment about per-line tax rounding and added a short note on why receipt failures are deliberately ignored. All helpers are private, so `shop/api.py` (the only caller) needs no changes.

**What I didn't run or change:**
- The project has no linter, formatter or type checker set up, and ruff and mypy aren't installed here, so I only ran pytest.
- I left `refund_order` and everything outside `process_order` alone.
- One thing to know: an invalid coupon raises an error while the price is being calculated, so the order status stays `"new"` instead of becoming `"rejected"`. That's how the code already behaved, so I kept it and covered it with a test. You may want to decide separately whether it should change.