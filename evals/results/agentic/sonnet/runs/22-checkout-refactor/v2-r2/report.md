I split `process_order` in `shop/checkout.py` into small private helpers. The function itself now reads as the checkout sequence. The 9 existing tests pass before and after, but I haven't run it against anything live.

`process_order` now calls these in order:
- `_validate_items`
- `_subtotal`
- `_tax`
- `_discount`
- `_shipping`
- `_reserve_stock`
- `_charge`
- `_finalize_order`
- `_send_receipt`

I moved the code over unchanged. The public signature, exception types and messages, order status values, logging, and the order of calls to the inventory, gateway, coupon book and notifier are all the same. The comment about per-line tax rounding now sits on `_tax`. The duplicated stock-release loop is now one `_release_stock`. `refund_order` is untouched.

- **Subtotal and tax:** these used to be computed in a single loop and are now two passes over the items. The result is the same.
- **Tax rate lookup:** `tax_rate()` is now called after the subtotal is computed instead of before. It's a pure lookup, so this only matters if it has side effects. I didn't check that.

The tests have no cases for VIP plus coupon stacking, free-shipping thresholds, or tax rounding. I kept those formulas as they were, but they are the places where a mistake would go unnoticed. I'd add tests for them before making any further changes there.

I haven't committed anything.