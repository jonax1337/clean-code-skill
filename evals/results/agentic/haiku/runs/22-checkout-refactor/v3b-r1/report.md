I split `process_order` into small private helpers in `shop/checkout.py`. Behavior is unchanged, and the public signature is the same. Nothing is committed.

**New shape:** `process_order` is now about 20 lines that read as the checkout steps: validate, total, reserve stock, charge, record payment, send receipt. The helpers are `_validate_items`, `_total_cents` (with `_subtotal_and_tax`, `_discount_cents`, `_coupon_discount_cents`, `_shipping_cents`), `_reserve_stock`, `_release_stock_and_mark`, and `_record_payment`. Constants, `refund_order`, and the tax-rounding comment are unchanged.

**Verification:**
- The existing suite had 9 tests, and they missed several behaviors. I added `tests/test_checkout_characterization.py` with 13 tests that pin the current behavior, including VIP discounts, per-line tax rounding, the free-shipping boundary, partial stock release, and the swallowed receipt error. I ran them against the original code first. One failed because of my own arithmetic error, which I fixed in the test.
- `pytest`: 22 passed (9 original + 13 new).
- Differential fuzz: I ran the original and refactored functions on 20,000 random orders, with random stock, coupons, VIP status, countries, and gateway and notifier failures. Outputs, order state, inventory logs, charges, receipts, and coupon usage matched in every case. I deleted the scratch script afterward.
- Ruff and mypy are not installed here, so I did not run them. I checked imports by hand.

**Found, not changed:** if the gateway raises something other than `PaymentDeclined` (for example a network error), the reserved stock is never released and the order status stays `new`. The characterization test `test_gateway_error_other_than_decline_propagates_and_keeps_the_reservation` pins this as-is. It looks like a real bug that leaks inventory, but fixing it changes production behavior, so I left it for a separate change.