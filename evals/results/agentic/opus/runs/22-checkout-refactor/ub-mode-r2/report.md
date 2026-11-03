I've split `process_order` into smaller functions. Its signature and observable behavior are unchanged, and all 22 tests pass. It now just runs the checkout steps in order:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_mark_paid(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

`_order_total` is built from small single-purpose functions: `_line_cents`, `_tax` (rounded per line, half-up, on the undiscounted price), `_coupon_percent`, `_discount` (coupon first, then VIP on what's left) and `_shipping`. Both failure paths share one `_release` helper to give the stock back. The business rules that were only in your head or in comments are now docstrings, e.g. "a failed receipt is logged, never raised: the customer has already been charged."

**How I made sure nothing changed:**
- **Tests written first:** the existing tests didn't cover a lot. I added 13 tests in `tests/test_checkout_pinned.py` and ran them against the original code before touching it. They cover:
  - the VIP discount on top of a coupon
  - the exact €50 free-shipping boundary, and a coupon pushing an order below it
  - per-line half-up tax rounding, including the default tax rate
  - stock already reserved being released when a later item is out of stock
  - the exact sequence of stock operations on success and on a declined payment
  - when the coupon is used up, and that it isn't on failure
  - a failed receipt not failing the order, plus the log output
  - bad quantities and bad coupons being rejected before any stock is touched
- **Mutation check:** the mutation tools the skill mentions aren't installed, so I wrote a throwaway script. It plants small bugs one at a time (flipping `<=` to `<`, `HALF_UP` to `HALF_EVEN`, removing a status change or a stock release, and so on) and checks the tests catch each one. All 12 were caught on the original code and all 18 on the new code. The first run also exposed a weak assertion in my receipt test, which I fixed.

One deliberate detail: when a payment is declined, the new code releases all of the order's items rather than a separately tracked list of reserved ones. That's equivalent, because reaching the payment step means every item was reserved, and the stock-operation test confirms it.

**Log:**
1. Read the checkout module, its collaborators and the tests; baseline was 9/9 passing.
2. Added the 13 tests above; 22/22 passed on the original code.
3. Ran the mutation script on the original code; one bug slipped through (the log's error details), so I tightened that assertion. Rerun: 12/12 caught. Fixed the script's Windows line-ending handling so the source file is restored byte-for-byte.
4. Commit `44afd75`: the new tests.
5. Refactored `shop/checkout.py`; 22/22 pass.
6. Ran 18 mutants against the new code: 18/18 caught.
7. Commit `6019c30`: the refactor.
8. Deleted the scratch script; the working tree is clean.

**Not pushed:** the repo has no remote configured, so both commits are only on your local `main`.