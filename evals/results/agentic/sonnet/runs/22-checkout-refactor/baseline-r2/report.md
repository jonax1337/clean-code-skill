I split `process_order` in `shop/checkout.py` into small private helpers. It now reads as a short outline of the checkout steps. The existing 9 tests pass. I haven't committed anything.

The helpers are:
- `_validate_items`
- `_subtotal_and_tax`
- `_discount_cents`
- `_shipping_cents`
- `_reserve_items`
- `_charge`
- `_finalize_order`
- `_send_receipt`

I also added `_release_all`, which replaces the release loop that appeared twice.

I moved the code over without changing it. Several things stay as they were:
- **Order of operations:** this covers the tax-rate lookup before the coupon check, and the stock reservation before the charge. It also covers commit, then coupon redemption, then the status update, then the receipt.
- **Failure behavior:** the rollback paths and the `order.status` values (`rejected`, `payment_failed`, `paid`) are the same. The same `OrderRejected` messages are raised with the same exception chaining.
- **Receipt errors:** a failed receipt send is still logged as a warning and doesn't fail the order.
- **Public interface:** the signature of `process_order` and `refund_order` are untouched.

I didn't read the tests, so I can't say how much of the failure and rollback behavior they exercise. Because this is live in production, it's worth a look at the diff and a staging run before you deploy.