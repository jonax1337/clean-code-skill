`process_order` is split into small helpers in `shop/checkout.py`. The public signature and the order of every side effect are unchanged, and all 19 tests pass. I left the changes uncommitted in the working tree, since you didn't ask for a commit.

**Refactor**

`process_order` is now a short sequence of steps:

```python
_validate(order)
total = _total_cents(order, customer, coupons)
reserved = _reserve_stock(order, inventory)
receipt_id = _charge(order, customer, gateway, inventory, reserved, total)
_record_payment(order, inventory, coupons, total)
_send_receipt(order, customer, notifier, receipt_id)
return receipt_id
```

- `_total_cents` builds on `_subtotal_and_tax` (per-line tax rounding, kept with its comment) and `_discount_cents` (coupon, then VIP).
- The two copies of the release loop are now one helper, `_release_stock`.
- `_charge` only releases stock on `PaymentDeclined`, as before. Other gateway errors still propagate without a release.

**Tests**

Before touching the code I added 10 characterization tests to `tests/test_checkout.py`. They cover the VIP discount, the free-shipping boundary (exactly 5000 and below it), shipping decided after the coupon, per-line half-up tax rounding, validation failures, a partial-reservation rollback, a non-decline gateway error, and a receipt failure that doesn't fail a paid order. All of them passed on the original code and still pass on the refactored code.

To check the tests can catch regressions, I broke the refactored code three ways and confirmed each one fails: banker's rounding for tax, an off-by-one on the free-shipping threshold, and no stock release on payment decline.

**Things I did not do**

- The skill's crapper, dryer and mutator tools are not installed here, so I did not run complexity, duplication or mutation reports. The mutation checks above were manual.
- I did not commit or push. The skill asks for commits and a push to main, but this session's rules only allow those when you ask. Say the word and I'll commit in small steps.

**Something to look at**

If the gateway raises anything other than `PaymentDeclined`, the reserved stock is never released and the order stays `new`. I pinned that current behavior in a test rather than changing it, since you asked for no behavior change. It may be worth a separate fix.