I split `process_order` in `shop/checkout.py` into small private helpers, and its behavior is unchanged as far as the tests can show. All 18 tests pass, both before and after the refactor. I haven't committed anything.

`process_order` now reads as a short sequence of steps:

1. `_validate_items` checks the order has items and positive quantities.
2. `_subtotal_and_tax` computes the subtotal and the per-line tax, which is rounded half-up and charged on the undiscounted price.
3. `_discount_cents` applies the coupon, then the VIP discount on what's left.
4. `_shipping_cents` decides shipping.
5. `_reserve_items` reserves stock and releases it again if anything is out of stock.
6. `_charge` charges the customer and releases the stock if the payment is declined.
7. `_finalize_order` commits stock, redeems the coupon, sets the status and total, and logs.
8. `_send_receipt` sends the receipt and only logs a warning if sending fails.

The refactor keeps the order of side effects, the error messages and the exception chaining exactly as before. It also leaves the public signature of `process_order` untouched. The only other edit to `checkout.py` is the extra `Item` import for type hints.

The existing 9 tests skipped many branches, so I added 9 characterization tests to `tests/test_checkout.py` and ran them against the old code before refactoring. They cover:
- the VIP discount stacking on a coupon
- the free-shipping threshold, with and without a discount
- per-line half-up tax rounding
- the default tax rate for unknown countries
- invalid quantity and invalid coupon
- rollback of a partial reservation
- a failing receipt not failing the order

The tests use fakes, so nothing was exercised against the real payment gateway, inventory or notifier. Please do a normal review and staging pass before you ship it.