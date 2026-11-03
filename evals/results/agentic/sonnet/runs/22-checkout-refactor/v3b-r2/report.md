I split `process_order` in `shop/checkout.py` into small private helpers, and its behavior is unchanged as far as the tests show. All 24 tests pass (`pytest`: 24 passed). Ruff and mypy aren't installed here, so I didn't run a linter or type checker.

`process_order` is now a short sequence of steps:

1. `_validate_items`
2. `_order_total`
3. `_reserve_items`
4. `_charge`
5. `_complete_order`
6. `_send_receipt`

`_order_total` builds on `_subtotal_and_tax` and `_discount`, and `_release_items` is shared by the two rollback paths. The order of side effects is the same as before, as are the exception types and messages, the order statuses, and the log output. The signature is the same too, so `shop/api.py` and other callers are unaffected. The comment about per-line tax rounding now sits on `_subtotal_and_tax`, where that logic lives.

**Tests:** the 7 existing tests missed most branches of this function. Before touching the code, I added 15 tests to `tests/test_checkout.py` that pin the current behavior, and confirmed they passed against the original code. They cover:
- invalid quantity and unknown coupon
- VIP discount, alone and stacked on a coupon
- the free-shipping threshold, just below, exactly at, and on the discounted amount
- per-line half-up tax rounding and the default tax rate
- rollback of a partial reservation
- the order of reserve and commit calls
- a declined payment not using up the coupon
- a failing receipt not failing the order

**Left alone:** `refund_order` and the rest of the module. I also didn't change the behavior that `_complete_order` and `_send_receipt` run after the charge, so a crash in `commit` or `redeem` would still leave a customer charged without a paid order. That is existing behavior, but you may want to look at it separately.

I haven't committed anything.