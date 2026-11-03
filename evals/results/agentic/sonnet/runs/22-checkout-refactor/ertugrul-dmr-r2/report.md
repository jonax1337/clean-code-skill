I split `process_order` in `shop/checkout.py` into small helpers. It keeps the same signature and now reads as a sequence of steps. All 9 existing tests pass, but I haven't deployed or run it anywhere beyond that.

`process_order` now runs these steps in order:
1. `_validate_items` checks for an empty order and for quantities that aren't positive.
2. `_calculate_total` works out the total from the subtotal, tax, discount and shipping. It uses `_calculate_tax` (per-line rounding, as before) and `_calculate_discount`. That in turn uses `_coupon_discount` for the coupon and then applies the VIP discount.
3. `_reserve_items` reserves stock, and on `OutOfStock` releases what it reserved and sets the status to `rejected`.
4. `_charge_or_release` charges the customer, and on `PaymentDeclined` releases the stock and sets the status to `payment_failed`.
5. `_finalize_paid_order` commits the stock, redeems the coupon, sets the status to `paid` and records the total.
6. `_send_receipt` sends the receipt, and a failure there is only logged.

**Behavior I preserved:**
- The order of side effects and of failure checks is the same. The tax rate is still looked up before the coupon is validated, and nothing is reserved until pricing has succeeded.
- The error messages, order statuses and rounding are unchanged.
- The VIP discount is still applied to the amount left after the coupon.
- `_release_items` receives `order.items` when a payment is declined. That is the same set that was reserved, because stock reservation only succeeds if every item is reserved.

**Style fixes:**
- Each helper takes three arguments, or five in `_charge_or_release`. That one is over the three-argument limit (F1), because it needs the order, customer, total, inventory and gateway together. I left it rather than add a wrapper type.
- The tax comment is now the docstring of `_calculate_tax`.
- The subtotal is a single `sum(...)`. It is computed separately from the tax loop, but gives the same values.

I haven't committed anything.