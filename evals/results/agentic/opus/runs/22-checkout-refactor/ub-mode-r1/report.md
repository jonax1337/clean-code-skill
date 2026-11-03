I've split `process_order` into small named steps, and its behavior is unchanged as far as I could test. It's committed locally but **not pushed**: the repo has no git remote, so the push failed.

**The new structure** (`shop/checkout.py`): `process_order` is now six lines, one per step:

```python
_validate(order)
total = order_total(order.items, tax_rate(customer.country), _coupon_percent(order, coupons), customer.vip)
_reserve_stock(order, inventory)        # all-or-nothing; releases earlier reservations on shortage
receipt_id = _charge(...)               # gives stock back on decline
_complete(order, inventory, coupons, total)
_send_receipt(...)                      # failure is only logged, never fails a paid order
```

- **Price math** is now a separate function, `order_total`, that only does arithmetic and touches nothing else. It's built from `_line_tax`, `_discounted` and `_shipping`, and the per-line tax rounding comment stays with it.
- **Coupon lookup** is in `_coupon_percent`, and the shared rollback is in `_release`.
- The steps run in the same order as before. Error messages, `order.status` values, exception chaining and log output are all the same. `refund_order` is untouched.

**How I checked it:**
1. **Pinned the current behavior first.** The existing tests didn't cover the VIP discount, the free-shipping threshold, per-line tax rounding, invalid quantities or coupons, partial-reservation rollback, keeping the coupon when an order fails, the status left after each rejection (`api.py` shows it to callers), or the swallowed receipt failure. I added 20 tests for these in `tests/test_checkout_pinned.py` and ran them against the original code. Three failed at first because I had miscalculated the expected values in the tests; the code was right, so I corrected the tests.
2. **Ran old and new side by side** on 20,000 random orders covering every outcome (paid, out of stock, payment declined, invalid input). I compared the return value, exception, status, total, inventory operations, charges, coupon uses and receipts: no differences.
3. **Checked that the tests catch real bugs.** I made 9 deliberate breaking edits by hand. One got through at first: removing the traceback from the receipt warning. I tightened that test, and now all 9 are caught. The CRAP-score, duplication and mutation tools your workflow mentions aren't installed, so I couldn't run them.

All 29 tests pass.

**Commits (local only, on `main`):**
- `eba98fa` adds the tests that pin current behavior.
- `c14d6d3` fixes the receipt-warning test so it catches a missing traceback.
- `ff80ca0` is the refactor itself.

To push, add a remote with `git remote add origin <url>` and run `git push origin main`.