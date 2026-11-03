I split `process_order` in `shop/checkout.py` into small private helpers. The existing 9 tests pass, but I haven't committed anything.

`process_order` now reads as a sequence of steps:

1. `_validate_items` checks the order has items and that quantities are positive.
2. `_subtotal_and_tax` computes the subtotal and the per-line rounded tax. I kept the comment explaining why tax is on the undiscounted price.
3. `_discount` applies the coupon and then the VIP discount.
4. `_shipping` charges shipping unless the discounted subtotal reaches the free-shipping threshold.
5. `_reserve_stock` reserves stock, and on `OutOfStock` releases what it reserved, sets the status to `"rejected"` and raises `OrderRejected`.
6. `_charge` charges the customer, and on a decline releases the stock, sets `"payment_failed"` and raises `OrderRejected`.
7. `_finalize_paid_order` commits stock, redeems the coupon, sets the status to `"paid"` and the total, and logs.
8. `_send_receipt` sends the receipt, and logs a warning instead of failing the order if sending breaks.

Behavior should be unchanged:

- **Order of side effects:** The calls happen in the original order. In particular, the coupon is still validated after tax is computed and before stock is reserved.
- **Messages and statuses:** Exception types, messages and status values are identical.
- **Public API:** `process_order` has the same signature, and I didn't touch `refund_order`.
- **Release logic:** The two duplicated release loops now share one `_release` helper.

I didn't add new tests. If you want more confidence before deploying, I can add tests for edge cases like VIP plus coupon, the free-shipping boundary, and a receipt failure.