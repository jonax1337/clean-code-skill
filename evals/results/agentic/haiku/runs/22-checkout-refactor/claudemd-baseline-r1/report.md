I split `process_order` in `shop/checkout.py` into small helpers. The public signature is unchanged and all 17 tests pass: the 9 existing ones and 8 new ones.

**What changed in `shop/checkout.py`**
- `process_order` now reads as the checkout steps: validate, price, reserve, charge, mark paid, send receipt.
- New private helpers: `_validate_items`, `_price_order` (returns a small `_Pricing` dataclass with `total` as a property), `_subtotal_and_tax`, `_discount_cents`, `_reserve_stock`, `_release`, `_mark_paid`, `_send_receipt`.
- The two duplicated release loops now go through `_release`.
- Arithmetic, the order of side effects, status strings, error messages and the logger name are unchanged. The per-line tax comment moved with its code.

**Tests added to `tests/test_checkout.py`**
I added characterization tests for paths the existing suite did not cover, and ran them against the original code before refactoring so they describe current behavior:
- zero quantity is rejected
- unknown coupon is rejected before any stock is touched
- VIP extra discount
- shipping threshold is checked after the coupon
- shipping is free at exactly the threshold
- tax is rounded per line
- a partial reservation is released when a later item is out of stock
- a failing receipt does not fail a paid order

**Things I noticed but did not change**
- If `gateway.charge` raises anything other than `PaymentDeclined`, the reserved stock is never released and the order status stays `"new"`. That looks like a stock leak, but fixing it would change behavior, so I left it. I can make that fix separately if you want it.
- I did not commit anything.