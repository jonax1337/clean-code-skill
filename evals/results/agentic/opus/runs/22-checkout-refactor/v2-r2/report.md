I've split `process_order` into small helpers, and all 18 tests pass, including 9 new ones I wrote against the original code before refactoring. Ruff and pyflakes aren't installed here, so no linter or formatter was run.

**Adding tests first.** The existing tests didn't cover several things that matter in production. I added tests to `tests/test_checkout.py` that pin down how the current code behaves:
- The VIP discount is applied after the coupon.
- Free shipping starts at exactly 5000, counted after discounts.
- Tax is rounded per line, not on the total.
- Orders with zero or negative quantities are rejected.
- An invalid coupon rejects the order before any stock is reserved, and the status stays `"new"`.
- When an item is out of stock, only the items already reserved are released.
- On success, stock is committed in item order and the coupon is redeemed once.
- If the receipt fails to send, the order stays paid and a warning is logged.

All of them passed on the old code, then passed again after the refactor.

**The new structure.** `process_order` now reads as a list of steps:

```python
_validate_items(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, total, inventory, gateway)
_complete_payment(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

The pricing logic is split into `_line_cents`, `_tax_cents`, `_discount_cents` and `_shipping_cents`. The code that gave stock back was duplicated in the out-of-stock and payment-declined paths; it's now one `_release_stock` helper. The function signature, error messages, status values, log lines and the order of side effects are all unchanged, so `shop/api.py` didn't need any changes.

**Two things I deliberately kept:**
- The per-line tax rounding comment, since it explains a requirement from the accounting export.
- The catch-all `except Exception` around sending the receipt. A paid order shouldn't fail because an email couldn't be sent. I added a one-line comment saying so, so nobody "fixes" it later.

**Not changed, but worth a look:** `test_coupon_discount_is_applied_and_redeemed` calls `coupons.redeem(...)` inside the test itself, which makes it hard to see what it's checking. My new commit/redeem test checks the same thing more directly. I didn't touch the existing test because that's outside this task.

Nothing is committed yet. Tell me if you'd like it on a branch with a PR.