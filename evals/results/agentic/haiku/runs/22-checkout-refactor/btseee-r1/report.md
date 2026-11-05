`process_order` is now a short sequence of named steps, and behavior is unchanged. All 17 tests pass, and the 20,000-scenario comparison against the original matched exactly.

**What changed in `shop/checkout.py`:**

`process_order` now reads as six steps: validate items, compute the total, reserve stock, charge, mark paid, send receipt. The pieces are:

- `_validate_items`
- `_total_cents`, which calls `_subtotal_and_tax`, `_discount_cents` (with `_coupon_discount_cents`), and `_shipping_cents`
- `_reserve_stock`, which reserves all items or releases the partial reservation before rejecting
- `_release_stock`
- `_mark_paid`
- `_send_receipt`

The per-line tax rounding comment moved with the tax code. `refund_order`, the constants, and the logger are untouched, so the public API is the same.

**Tests added to `tests/test_checkout.py`:** I wrote these against the original code first, and they passed there. They cover the paths the existing tests missed: VIP discount alone and combined with a coupon, free shipping, unknown-country tax, invalid coupon, zero quantity, partial stock rollback across two items, and a failing receipt that doesn't fail the order.

**Verification:**
- `pytest`: 17 passed, before and after the refactor.
- Differential check: I kept a copy of the original module outside the repo and ran both versions over 20,000 random scenarios. I compared return values, exception types and messages, exception causes, order status and total, gateway charges, notifier calls, the inventory log, and coupon state. Every scenario matched.

I did not commit anything.

**Existing behavior I kept on purpose, which you may want to look at separately:** if the gateway raises something other than `PaymentDeclined` (a network error, for example), the reserved stock is never released and the order status is not updated. The original code does this too, so I preserved it. Fixing it would be a behavior change, and it should go through its own review.