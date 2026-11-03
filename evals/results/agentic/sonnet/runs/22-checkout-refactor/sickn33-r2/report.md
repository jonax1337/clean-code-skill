I split `process_order` in `shop/checkout.py` into small helpers. It now reads as a short sequence of steps. The 9 existing tests passed before the change and pass after it. I haven't committed anything.

`process_order` now calls these in order:
- `validate_order`
- `compute_subtotal_and_tax`
- `compute_discount`
- `compute_shipping`
- `reserve_stock`
- `charge_customer`
- `finalize_paid_order`
- `send_receipt_quietly`

There is also a small `release_stock` helper. It replaces the release loop that was written out twice, once for out-of-stock and once for a declined payment.

I moved the code over without changing it, so these behaviors are the same as before:
- **Order of operations:** `tax_rate` is still called before the coupon is checked, so an unknown country still fails before an invalid coupon does.
- **Error handling:** the same exceptions and messages are raised, and `order.status` is set before each `OrderRejected`. Only `OutOfStock` and `PaymentDeclined` are caught, as before.
- **Failure cleanup:** stock is released in the same cases as before. If a reservation fails partway through, only the items already reserved are released.
- **Receipt failures:** any exception from sending the receipt is still logged as a warning and does not fail the order.
- **Public API:** `process_order` keeps the same signature and return value, and `refund_order` is untouched.

The existing tests are the only check on the unchanged behavior. I didn't add new ones, so I'd read the diff once for anything the tests don't cover, such as the exact log messages.

I left the `reserved` list typed as plain `list` to avoid adding imports. You could tighten it to `list[OrderItem]` if you have that model.