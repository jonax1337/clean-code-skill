I split `process_order` in `shop/checkout.py` into small helpers. The 9 existing tests pass. I haven't committed anything.

`process_order` now reads as a short sequence of steps:

1. `_validate_items`
2. `_subtotal_and_tax`
3. `_total_discount`
4. `_shipping_cents`
5. `_reserve_items`
6. `_charge_customer`
7. `_finalize_paid_order`
8. `_send_receipt_best_effort`

A small `_release_items` helper replaces the release loop that was written out twice.

The behavior should be unchanged. I kept the order of every step, so side effects and exceptions happen in the same sequence. That covers:
- the same error messages and the same `status` values;
- the same `raise ... from error` chaining;
- the item that hit `OutOfStock` is still not released, because it was never reserved;
- the receipt is still best-effort: any failure is logged as a warning and doesn't affect the return value.

I didn't touch `refund_order`, the constants, or the public signature. I also didn't add tests. The existing tests may not cover every failure path, such as coupon redemption or the receipt failure. If you want more safety for production, I can add tests for those paths.