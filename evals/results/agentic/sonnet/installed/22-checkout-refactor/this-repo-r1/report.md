I split `process_order` in `shop/checkout.py` into small private helpers, and its behavior is unchanged. All 28 tests pass (`python -m pytest`), and the 19 new ones also passed against the original code before I touched it. I didn't run a linter because none is configured (`ruff` isn't installed here).

`process_order` is now a short outline of the steps, in the original order:

1. `_validate_items` checks that there are items and that quantities are positive.
2. `_order_total` calculates the total. It uses `_tax_cents` for per-line tax and `_discount_cents` for the coupon and VIP discounts. Shipping stays inline in `_order_total`.
3. `_reserve_stock` reserves stock, using `_release_stock` to undo a partial reservation.
4. `_charge` charges the customer and releases the stock if the payment is declined.
5. `_complete_order` commits stock, redeems the coupon and marks the order paid.
6. `_send_receipt` sends the receipt, and a failure there is only logged.

The public signature, error messages, order statuses, call order on inventory, coupons and gateway, and the log output are all as before. I also left `refund_order` alone.

The existing tests didn't cover most of the pricing and failure paths, so I added `tests/test_checkout_characterization.py` before refactoring. It covers:
- VIP discounts and VIP combined with a coupon
- invalid, exhausted and unredeemed coupons
- the free-shipping threshold
- per-line half-up tax rounding and the rate for each country
- invalid quantities
- partial stock release
- the exact order of inventory calls
- a receipt failure not failing the order

I didn't change the pricing rules, even where they look surprising. Tax is charged on the undiscounted price and discounts round down. The new tests pin those rules, so changing them later will show up as a failing test.