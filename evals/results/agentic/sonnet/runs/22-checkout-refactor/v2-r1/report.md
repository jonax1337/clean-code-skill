I split `process_order` in `shop/checkout.py` into small helpers. The 9 existing tests passed before and after the change. I haven't committed anything.

`process_order` now reads as the sequence of checkout steps. Each helper holds one step:

- **`_validate_items`:** rejects empty orders and non-positive quantities.
- **`_subtotal_and_tax`:** computes the subtotal and the per-line rounded tax. The comment explaining the tax rounding moved with it.
- **`_discount_cents`:** applies the coupon, then the VIP discount.
- **`_reserve_items`:** reserves stock. On `OutOfStock` it releases what it reserved, sets the status to `rejected` and raises `OrderRejected`.
- **`_charge`:** charges the customer. On `PaymentDeclined` it releases the reservation, sets `payment_failed` and raises.
- **`_release_items`:** shared by both failure paths, which used to repeat the same release loop.
- **`_send_receipt`:** sends the receipt and still only logs a warning if sending fails.

I kept the order of side effects identical: validation, tax, coupon lookup, reserve, charge, commit, redeem, status, then receipt. The error messages, status strings and exception chaining are unchanged. The public signature of `process_order` is unchanged, and `refund_order` is untouched.

The tests pass, but I didn't check how thoroughly they cover the failure paths (stock rollback, declined payment, receipt failure). For a production-critical function, it's worth checking that before you deploy.