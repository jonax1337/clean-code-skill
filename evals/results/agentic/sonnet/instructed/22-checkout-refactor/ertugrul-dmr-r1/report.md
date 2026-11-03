I refactored `process_order` in `shop/checkout.py`. The 9 existing tests pass, but I haven't committed anything. The tests don't cover every branch, so I only checked the other branches by reading the code.

`process_order` is now a short top-level flow that calls small helpers:

- **`_validate_items`**: the empty-order and bad-quantity checks.
- **`_price_order`**: computes the total, using `_line_cents`, `_tax_cents`, `_coupon_discount_cents` and `_shipping_cents`.
- **`_reserve_stock`, `_release_stock`, `_commit_stock`**: the stock handling. A failed reservation still releases what was reserved, sets `rejected` and raises `OrderRejected`.
- **`_mark_paid`**: sets the status and total and writes the log line.

The signature of `process_order` is unchanged, so `shop/api.py` and the tests need no edits. The main flow keeps the payment-decline handling, the coupon redemption and the best-effort receipt send inline. Pulling those out would have meant helpers with four or more arguments.

I kept the order of side effects the same:

- Everything that can reject an order before stock is touched still runs first.
- The coupon is still only redeemed after a successful charge.
- The "paid" log line still comes before the receipt attempt.
- A failed receipt send still only logs a warning.

On payment failure the old code released the items it had reserved. The new code releases `order.items`. These are the same list at that point, because reservation only gets that far if every item was reserved.

The tax comment now sits on `_tax_cents` as a docstring.

Before you deploy, I'd add a couple of tests for the VIP discount, free-shipping threshold and per-line tax rounding.