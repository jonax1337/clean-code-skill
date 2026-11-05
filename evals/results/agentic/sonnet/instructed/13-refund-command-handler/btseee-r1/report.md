I added `RefundOrder(orderId, amount)` with its handler, and the full suite passes (27 tests, 7 of them new). I haven't committed anything.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`, and the order's status is never changed.
- **Cap:** the cap is `amountPaid`, not `total`. Orders can be underpaid, for example when a voucher covered part of the total, so capping at the total would let a customer get back more than they paid. A refund that would push the running total of refunds past `amountPaid` fails with `INVALID_INPUT`. Refunding exactly up to `amountPaid` is allowed.
- **Recording:** each refund is added to the order's `amountRefunded`, through a new `Order.recordRefund`.
- **Input and lookup:** the amount must be positive with at most two decimals, like `PayOrder`. An unknown order returns `NOT_FOUND`.

I registered the handler in `OrderServices.createBus` and added a `RefundOrder` row to the commands table in `README.md`. The new tests are in `RefundOrderHandlerTest`.