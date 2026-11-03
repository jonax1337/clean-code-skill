I split `process_order` in `shop/checkout.py` into small private helpers. The function itself is now a short list of steps. The 9 existing tests pass, but I haven't run it against anything beyond them.

`process_order` now calls these in order:
- `_validate_items` checks for an empty order and for quantities of zero or less.
- `_calculate_total` combines the next two helpers and adds shipping.
  - `_subtotal_and_tax` does the per-line tax rounding and keeps its explanatory comment.
  - `_discount` applies the coupon and then the VIP discount.
- `_reserve_stock` reserves stock, and on `OutOfStock` releases what it reserved, marks the order `rejected` and raises.
- `_charge` charges the customer, and on a decline releases the stock, marks the order `payment_failed` and raises.
- `_release_stock` is the shared release loop for those two failure paths.
- `_finalize_paid_order` commits stock, redeems the coupon, sets the status to `paid` and total, and logs.
- `_send_receipt` sends the receipt and logs a warning if that fails, without failing the order.

I moved the code over without changing it:
- **Order of side effects:** the sequence is the same. An invalid coupon still raises before any stock is reserved, and the coupon is only redeemed after a successful charge.
- **Unchanged details:** the error messages, status values, the receipt failure handling and the arithmetic (integer division and `ROUND_HALF_UP`) are the same.
- **Not touched:** `refund_order`, the constants and the public signature of `process_order`.

The existing tests don't cover a few paths: VIP discount, free shipping, an invalid coupon, a quantity of zero or less, and a failing notifier. I read those paths by hand rather than testing them. If you want extra confidence for production, I can add tests for them and run them against both the old and new versions.

I haven't committed anything.