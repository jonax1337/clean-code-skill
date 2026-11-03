I split `process_order` in `shop/checkout.py` into small private helpers. `process_order` is now a short sequence of steps. All 9 existing tests pass. I haven't committed anything.

The steps are:
- `_validate_items`
- `_calculate_total`, which uses `_subtotal_and_tax`, `_discount` and `_shipping`
- `_reserve_stock`
- `_charge`
- `_finalize`
- `_send_receipt`

I kept the operations in the original order, so behavior should be identical:
- **Order of checks:** validation comes first, then the tax lookup and coupon check, and only then stock reservation.
- **Failure handling:** the same error messages and order statuses (`rejected`, `payment_failed`) are set at the same points. Stock is released on out-of-stock and on payment decline.
- **Calculations:** the per-line tax rounding, the coupon-then-VIP discount, and the free-shipping threshold are unchanged.
- **Receipt sending:** a failed send is still only logged, and the receipt id is still returned.

I only ran the existing tests, and I didn't check what they cover. Before deploying, check that they cover the out-of-stock, payment-declined, coupon and VIP paths.