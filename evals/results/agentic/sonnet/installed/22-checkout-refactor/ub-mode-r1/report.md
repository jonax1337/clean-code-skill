I split `process_order` in `shop/checkout.py` into small private helpers. `process_order` itself is now a short sequence of calls. All 9 existing tests pass. I haven't committed anything.

The helpers are:
- `_validate_items`
- `_subtotal_and_tax`
- `_discount_cents`
- `_shipping_cents`
- `_reserve_stock`
- `_release_stock`
- `_charge`
- `_finalize_paid_order`
- `_send_receipt`

**Behavior:**
- The order of side effects is the same as before. Validation comes first, then the tax lookup, then the coupon check, then stock reservation, the charge, the commit and coupon redemption, the status update and log line, and finally the receipt.
- Error messages, order statuses, exception chaining (`from error`) and the receipt step swallowing and logging failures are all unchanged.
- The tax and discount arithmetic is the same, including per-line tax rounding on the undiscounted price.
- Public signatures and `refund_order` are untouched.

**Tests:** the existing tests don't cover VIP discounts, invalid coupons, invalid quantities, free shipping, or a receipt send that fails. I moved that code as-is without changing it, but those paths are not checked by tests. If you want more safety before deploying, I can add characterization tests for them. I'd write them against the original code first and then confirm they still pass after the refactor.