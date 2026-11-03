I split `process_order` into small private helpers in `shop/checkout.py`. Behavior is unchanged: all 17 tests pass, and a randomized comparison against the original found no differences.

**What changed**

`process_order` now reads as the checkout steps: validate, price, reserve, charge, then commit, redeem and send the receipt. The helpers are:
- `_validate_items`
- `_total_cents`, which calls `_discount_cents`, `_tax_cents` and `_shipping_cents`
- `_reserve_stock`
- `_release_stock`, which replaces two copies of the same release loop
- `_send_receipt_quietly`

The public signature, the constants and `refund_order` are untouched.

One change is a simplification, not a literal move. On a payment decline, the original released the `reserved` list. I now release `order.items`. These are the same items, because the code only reaches the charge after every reservation succeeded.

**Tests added before the refactor**

The existing tests missed several branches, so I added characterization tests to `tests/test_checkout.py` and ran them against the original code first:
- zero quantity
- unknown coupon
- VIP discount stacked on a coupon
- free-shipping threshold
- per-line tax rounding
- out-of-stock on a later item releasing the earlier ones
- a failing receipt not failing the order
- a gateway error other than a decline

**Verification**
- `pytest`: 9 passed before, 17 passed after the refactor.
- Differential run: the original and refactored functions on 20,000 random orders, comparing results, exceptions, order state, inventory log, gateway and notifier calls, and coupon state. 0 mismatches.
- No linter or type checker is installed in this environment, so I did not run one.

**Things to know**
- The gateway-error test pins existing behavior that may be a bug. When the gateway fails with anything other than a decline, the stock stays reserved and the order stays `new`. I left it as-is because the task was behavior-preserving. The test is named and commented as a characterization test. If you want that fixed, it's a separate change.
- Nothing is committed.