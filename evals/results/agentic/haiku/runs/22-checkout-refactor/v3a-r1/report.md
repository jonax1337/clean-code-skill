`process_order` is split into small private helpers in `shop/checkout.py`. The public signature is unchanged, and all 18 tests pass, including the 9 existing ones and 9 new characterization tests. I didn't commit anything.

**What changed**

`process_order` now reads as six steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_mark_paid(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

The helpers are `_validate_items`, `_order_total`, `_subtotal_and_tax`, `_discount`, `_reserve_stock`, `_charge`, `_mark_paid`, `_send_receipt` and `_release_stock`. The helpers sit below `process_order` in call order. The ordering of side effects is the same as before: validation, pricing, reservation, charge, commit, receipt. Error messages, status values, log lines and the per-line tax comment are unchanged.

**Behavior safety**

The existing tests covered only the main paths, so I wrote characterization tests before touching the code. They cover:
- VIP discount applied after the coupon
- free shipping at exactly 5000
- per-line tax rounding
- default tax rate for an unknown country
- invalid quantity and invalid coupon, both rejected before any stock is reserved
- partial reservation released on out-of-stock
- coupon not redeemed when payment is declined
- a failing receipt notifier not failing a paid order

All of them passed against the original code before I refactored, which confirms they describe current behavior. They pass unchanged afterwards. The new tests are in `tests/test_checkout.py` and should stay in the diff.

**Left alone**
- `refund_order` in the same file. It's already short, and it was out of scope.
- The `checkout.py` module-level constants and the `shop/api.py` caller, which didn't need changes.

**Not done**
- I haven't run a linter or type checker because neither is set up in the project. The import list was checked by reading.
- The refactor isn't tested against real gateway or inventory implementations, only the fakes in `conftest.py`.