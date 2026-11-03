I refactored `process_order` in `shop/checkout.py` into small private helpers. The 20 tests pass (`python -m pytest`), and that includes the 11 I added before refactoring. I didn't run `ruff` or `mypy` because neither is installed here.

**Tests first.** The existing 9 tests missed many branches, so I added 11 characterization tests to `tests/test_checkout.py` and ran them against the original code. They cover:
- invalid quantity and invalid coupon
- the VIP discount stacking after the coupon
- free shipping at the threshold, and shipping charged when a discount drops the total below it
- per-line half-up tax rounding, and the default tax rate for an unknown country
- rollback of a partial stock reservation
- release of all items when payment is declined, with the coupon not redeemed
- commit order of the stock
- a failing receipt not failing a paid order

**The refactor.** `process_order` now reads as the sequence of steps:
1. Validate the items.
2. Compute subtotal, tax, discount and shipping.
3. Reserve stock.
4. Charge the customer.
5. Finalize the paid order.
6. Send the receipt.

The helpers are `_validate_items`, `_subtotal_cents`, `_tax_cents`, `_discount_cents`, `_shipping_cents`, `_reserve_stock`, `_release_stock`, `_charge`, `_finalize_paid_order` and `_send_receipt`.

**Behavior preserved:**
- The public signature and exception messages are unchanged.
- Side effects happen in the same order, and the inventory log is asserted in the tests.
- The comments on tax rounding, discount order and the receipt `except Exception` moved onto the helpers they describe.
- The rounding is still done per line.

I didn't touch `refund_order`, the other modules, or the helpers' naming style. The only change outside `process_order` is the `Item` import.

Because this is live, I'd also run it through your usual staging checks before deploying.