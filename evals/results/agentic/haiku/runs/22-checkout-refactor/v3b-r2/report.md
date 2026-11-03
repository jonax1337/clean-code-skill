I split `process_order` into smaller helpers in `shop/checkout.py`. The public signature, constants, log messages, and the order of stock, gateway, and coupon calls are unchanged. All 20 tests pass.

`process_order` is now a short sequence of steps:

1. `_check_items`: rejects empty orders and non-positive quantities.
2. `_price_items`: returns subtotal and per-line tax. The rounding comment moved here with the code.
3. `_discount_cents`: coupon and VIP discount.
4. `_shipping_cents`: the free-shipping threshold.
5. `_reserve_stock`: reserves each item and rolls back on `OutOfStock`.
6. `_charge`: charges the gateway and releases stock on `PaymentDeclined`.
7. `_record_payment`: commits stock, redeems the coupon, and marks the order paid.
8. `_send_receipt`: sends the receipt and logs, without failing the checkout, if sending fails.

`_release_stock` is a small shared helper for the two rollback paths.

**Tests:** The original code had 9 tests. Before touching the refactor, I added 11 characterization tests to `tests/test_checkout.py` that pin the branches the refactor touches: VIP discount after coupon, free-shipping threshold, per-line tax rounding, unknown country tax, zero quantity, unknown and exhausted coupons, the exact reserve/commit call order, rollback of a partial reservation, a failed receipt, and an unexpected gateway error. All 20 passed on the original code and still pass after the refactor (`python -m pytest -q`: 20 passed).

**Not run:** ruff and mypy are not installed in this environment, so I did not run them.

**Something to look at:** `test_unexpected_gateway_error_propagates_and_keeps_the_reservation` pins current behavior. If the gateway raises anything other than `PaymentDeclined` (a timeout, say), the stock stays reserved and the order stays `"new"`. That looks like a leak in production, so I kept it as-is. Fixing it would change behavior, so I left it for you to decide.

Nothing is committed.