I split `process_order` into small helpers. Its signature and behavior are unchanged.

**Tests first.** The existing tests didn't cover many of the rules, so before touching the code I added 12 tests to `tests/test_checkout.py` that pin down what it does now. All 21 tests (9 old, 12 new) passed against the original code before I refactored. The new tests cover:
- rejection of zero quantities
- an invalid coupon being rejected before any stock is reserved, with the status left at `"new"`
- tax rounded half-up on each line, using the customer's country
- the VIP discount applied after the coupon and rounded down
- the free-shipping cutoff at exactly 5000 cents (free) and 4500 (charged)
- stock that was already reserved being given back when a later item is out of stock
- every item reserved before any is committed
- the coupon not being used up when payment fails
- a failed receipt send not failing the order

**Refactoring.** `process_order` now reads as six steps:

```python
_validate_items(order)
total = _order_total(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge(order, customer, inventory, gateway, total)
_complete_payment(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
```

- The price calculation is split into `_line_cents`, `_tax`, `_discount` and `_shipping`.
- The two places that gave stock back now share one `_release` helper. When payment fails it releases `order.items`. That is the same list the old code released, because by then every item had been reserved.
- I kept the existing comment on tax rounding. I added two short comments to explain why the coupon is applied before the VIP discount, and why a failed receipt send is only logged.

**Checks**
- `pytest`: 21 passed after the final edit.
- `ruff` isn't installed here, so I didn't run a linter or formatter, and there is no type checker set up.
- `checkout.py` went from 97 to 134 lines because each helper has its own signature.
- Python wrote the files with Windows line endings, so I converted them back to LF. The diff contains no line-ending changes.

**Left as is**
- `refund_order` was already small.
- When a coupon is invalid, the order status is never set to `"rejected"`, unlike the out-of-stock case. That may be unintended, but changing it would change behavior, so a test now pins the current behavior instead.

Nothing is committed yet. Say if you want me to commit it on a branch.