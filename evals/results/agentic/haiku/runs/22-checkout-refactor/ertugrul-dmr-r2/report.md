I split `process_order` in `shop/checkout.py` into small helpers. The public function and its signature are unchanged, and it is now a short sequence of steps. Nothing is committed.

`process_order` now reads as: validate items → compute total → reserve stock → charge → mark paid → send receipt. The helpers are:
- `_validate_items`
- `_order_total_cents`, which calls `_subtotal_cents`, `_discount_cents`, `_tax_cents` and `_shipping_cents`
- `_reserve_stock`, which rolls back on out-of-stock
- `_charge`, which rolls back on decline
- `_mark_paid`
- `_send_receipt`
- `_release_items`

The per-line tax rounding comment moved to `_tax_cents`, where it applies. `refund_order` is untouched.

**Behavior check:**
- The 9 existing tests pass.
- I also compared the original and refactored functions on 20,000 randomized orders. The comparison covered return values, exception types and messages, order status and totals, inventory log, gateway charges, receipts, and coupon redemptions. All 20,000 matched, including 2,424 paid orders. The rest were rejection or failure paths.

Two things I did not change, which you may want to know about:
- The receipt-failure log still uses `exc_info`, so a failed receipt email logs a full traceback. That matches the original.
- The original had no test for a non-`OutOfStock` error from `inventory.reserve`. It is not rolled back in either version, so I preserved that. If that is a real gap, it is worth a separate fix.