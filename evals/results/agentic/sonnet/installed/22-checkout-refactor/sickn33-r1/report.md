I split `process_order` in `shop/checkout.py` into small private helpers. The existing 9 tests pass. I haven't committed anything.

`process_order` now reads as a short outline of the steps:
1. `_validate_items`
2. `_subtotal_and_tax`
3. `_discount_cents`
4. `_shipping_cents`
5. `_reserve_items`
6. `_charge`
7. `_finalize_order`
8. `_send_receipt`

I moved each block over unchanged, so behavior should be identical. That covers:
- the order of the steps (an invalid coupon is still rejected before any stock is reserved);
- the per-line tax rounding;
- the exact error messages and `order.status` values;
- the stock release on out-of-stock and on payment decline;
- the fact that a failed receipt only logs a warning.

The public signature of `process_order` is the same, and `refund_order` is untouched.

The tests passing is only partial evidence. I didn't check how much of the VIP, coupon and free-shipping paths they cover. Because this is live in production, I'd look at that before deploying.