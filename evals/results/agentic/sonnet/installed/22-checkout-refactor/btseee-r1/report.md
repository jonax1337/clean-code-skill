I split `process_order` in `shop/checkout.py` into small private helpers. It should behave exactly as before. The 9 existing tests pass before and after the change. I haven't committed anything.

`process_order` now reads as a short sequence of steps:

1. `_validate_items` rejects empty orders and non-positive quantities.
2. `_subtotal_and_tax` totals the lines and applies the per-line tax rounding. The comment about the accounting export moved here with it.
3. `_discount` applies the coupon and then the VIP discount.
4. `_shipping` returns the shipping cost.
5. `_reserve_items` reserves stock, and on `OutOfStock` releases what it reserved and marks the order `rejected`.
6. `_charge` charges the customer, and on `PaymentDeclined` releases the stock and marks the order `payment_failed`.
7. `_finalize_order` commits the stock, redeems the coupon, marks the order `paid` and logs it.
8. `_send_receipt` sends the receipt, and a failure is only logged as a warning.

- **Unchanged behavior:** The order of side effects and which errors get raised are the same. `tax_rate` is still called before the coupon is checked, and the order status is still set before the `OrderRejected` is raised. The exception messages and the `from error` chaining are unchanged. The only new code is a small `_release_all` helper that replaces the duplicated release loops.
- **Public API:** The signature of `process_order` and the rest of the module (`refund_order` and the constants) are untouched.
- **Test coverage:** I didn't check how well the 9 tests cover the failure paths, such as stock released after a declined payment or a receipt failing to send. Look at that before you deploy, because passing tests only prove what they cover.