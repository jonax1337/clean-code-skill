I split `process_order` in `shop/checkout.py` into small helpers, and behavior is unchanged as far as the tests show. All 21 tests pass.

`process_order` now reads as a short list of steps:

```python
_validate_items(order)
total = _total_cents(order, customer, coupons)
_reserve_stock(order, inventory)
receipt_id = _charge_or_release(order, customer, total, inventory, gateway)
_complete_order(order, total, inventory, coupons)
_send_receipt(order, customer, receipt_id, notifier)
return receipt_id
```

Each step is its own private helper. Pricing is split into `_tax_cents`, `_discount_cents` and `_total_cents`, and the stock rollback in `_release_stock` is shared by the two failure paths. The order of side effects is the same as before. Every check that can reject an order, including the coupon, still runs before any stock is reserved. The coupon is only redeemed after a successful charge. Receipt failures are still logged and swallowed. The rationale comment about per-line tax rounding moved into `_tax_cents`. Public signatures, exception types and messages, and logging are unchanged.

**Tests:** the 9 existing tests didn't cover most of the branches, so I added 12 characterization tests to `tests/test_checkout.py`. They cover:
- the VIP discount, alone and stacked with a coupon
- the free-shipping boundary, at 5000 and at 4999
- half-up tax rounding per line, and the default tax rate for unknown countries
- invalid coupons and invalid quantities
- stock rollback after a partial reservation
- the reserve-then-commit order
- no coupon redemption on a declined payment
- a failing notifier not failing the order

I ran them against the original code before refactoring, and they passed there too. `pytest` gives 21 passed after the refactor. `ruff` and `mypy` aren't installed here, so I didn't run a linter or type check.

I left `refund_order` and the rest of the module alone. One thing I noticed but didn't change: the "tax is computed on the undiscounted price" rule is pinned by the tests but looks unusual. It's worth confirming with whoever owns the accounting side.

I haven't committed anything.