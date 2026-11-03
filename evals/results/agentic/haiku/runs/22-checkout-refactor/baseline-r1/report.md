I refactored `process_order` in `shop/checkout.py` into small helpers. All 15 tests pass, including 6 new ones I added first to pin the branches the existing tests didn't cover.

**What changed**

- `process_order` is now a short sequence of steps: validate, price, reserve stock, charge, mark paid, send receipt.
- The helpers are `_check_items`, `_price_order`, `_subtotal_and_tax`, `_discount`, `_shipping`, `_reserve_stock`, `_release_stock`, `_charge`, `_mark_paid` and `_send_receipt_quietly`.
- A small frozen dataclass `_Price` holds the subtotal, tax, discount and shipping, and computes `total`.
- `refund_order` is untouched. The public signature of `process_order` is unchanged.

**Behavior preserved**

I kept the order of checks and side effects identical, since that is what production depends on:
- Validation runs before any pricing, and the coupon check still happens before any stock is reserved.
- Tax is still rounded per line and charged on the undiscounted price.
- The VIP discount is still applied after the coupon discount.
- Stock is released on out-of-stock and on payment decline, and nothing else is touched in those paths.
- Coupon redemption and commit still happen after a successful charge.
- A failing receipt is still logged and swallowed. The logger name is unchanged.

**Tests added (`tests/test_checkout.py`)**

They cover VIP discount, free shipping above the threshold, non-positive quantity, invalid coupon, partial out-of-stock release, and a failing receipt. I ran them against the original code first, and they passed there, so they describe current behavior rather than my reading of it.

**Not verified**

I ran pytest and a compile check on Python 3.12, but I did not run the refactored code against live data or a production-like environment. Nothing is committed; the changes are in the working tree for you to review.