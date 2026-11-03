`process_order` in `shop/checkout.py` is now a short top-to-bottom flow. The checks are in separate helpers, and behavior is unchanged as far as the tests can show. `pytest` gives 27 passed, run after the last edit. Before the refactor, the 9 existing tests plus my 18 new ones passed on the original code. `ruff` and `mypy` aren't installed here, so I didn't run a linter, formatter or type check.

**What the code looks like now**
- `process_order` keeps the order of side effects: validate, price, reserve, charge, commit, redeem the coupon, set status, log, send the receipt.
- Pricing is split into `_order_total`, `_tax_cents`, `_discount_cents` and `_shipping_cents`. The tax comment (per-line rounding, taxed on the undiscounted price) now sits on `_tax_cents`, where it applies.
- Stock handling is split into `_reserve_all` and `_release_all`. `_reserve_all` releases what it reserved and re-raises `OutOfStock`; `process_order` still sets `status = "rejected"` and raises `OrderRejected`.
- The receipt send is in `_send_receipt`. It still swallows and logs failures, because the order is already paid by then.
- Public signatures, exception types, messages and the order of calls to inventory, gateway and coupons are the same.

**New tests**
The existing tests didn't cover most branches, so I added `tests/test_checkout_characterization.py` first and checked it against the unchanged code. It pins:
- invalid quantity, and unknown or exhausted coupons
- VIP discount, alone and stacked on a coupon
- the free-shipping threshold, including after discounts
- per-line half-up tax rounding and the tax rate per country
- rollback of a partial reservation
- the exact inventory call order
- that a declined payment doesn't redeem the coupon
- that a failing notifier doesn't fail the order

**Left alone**
- `refund_order` and everything outside `checkout.py`.
- Nothing is committed.