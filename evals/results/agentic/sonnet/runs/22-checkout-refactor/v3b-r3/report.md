I've split `process_order` in `shop/checkout.py` into small private helpers, and behavior is unchanged as far as the tests can show. All 25 tests pass, 9 existing and 16 new. I didn't run a linter because `ruff` isn't installed here, and I didn't run a type checker.

**Tests first.** The existing tests missed most of the risky paths, so I added `tests/test_checkout_characterization.py` and ran it against the untouched original; it passed. It covers:
- invalid quantity and unknown or exhausted coupons, which are rejected before any stock is touched
- VIP discount stacked on a coupon
- the free-shipping boundary (4999 vs 5000, judged after discounts)
- per-line half-up tax rounding, and the default tax rate for an unknown country
- the exact reserve, release and commit sequence on out-of-stock and declined payment
- the coupon being redeemed only on success
- a failing receipt not failing the order

**Refactor.** `process_order` is now a short outline: validate, compute the total, reserve stock, charge, finalize, send the receipt. The helpers are `_validate_items`, `_order_total_cents`, `_tax_cents`, `_discount_cents`, `_reserve_stock`, `_release_stock`, `_charge`, `_finalize_paid_order` and `_send_receipt`.
- The public signature, exception types and messages, order statuses, and the sequence of inventory, gateway and coupon calls are the same.
- The rationale comment about tax rounding moved to `_tax_cents`.
- I also imported `Item` for a type hint and replaced the subtotal and tax loops with `sum`.

**One internal change.** Tax is now calculated before the coupon is checked, not after. It's a pure calculation, so nothing outside can observe the difference.

I left `refund_order`, `api.py` and the other modules alone. The changes are uncommitted in the working tree.