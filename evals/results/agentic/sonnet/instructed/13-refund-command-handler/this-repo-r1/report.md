`RefundOrder(orderId, amount)` is in and registered on the command bus. `java tools/RunTests.java` ran 29 tests and all passed, including the 9 new ones for refunds.

The handler (`RefundOrderHandler`) rejects a refund in these cases:
- **Status:** the order isn't shipped or delivered. The error is `INVALID_STATE`.
- **Cap:** the refund plus earlier refunds would exceed what the customer paid. The error is `INVALID_INPUT`. The cap uses `amountPaid`, not `total`, so an order paid at 80.00 of 100.00 can only be refunded 80.00 in total.
- **Input:** the amount is zero or negative, has more than two decimals, or the order ID is blank. These use the same validation as `PayOrder`.
- **Unknown order:** the error is `NOT_FOUND`.

A successful refund adds the amount to `amountRefunded` through a new `Order.recordRefund`, and the status stays as it was.

The new tests are in `RefundOrderHandlerTest`. They cover shipped and delivered orders (status unchanged), partial refunds adding up to the amount paid, and refunds over the cap. They also cover paid-only and cancelled orders, a zero amount, and an unknown order.

I didn't add any locking, so two refunds submitted at the same moment could both pass the cap check. I only read the in-memory repository's interface, not its internals, so I can't say whether that matters for your setup.