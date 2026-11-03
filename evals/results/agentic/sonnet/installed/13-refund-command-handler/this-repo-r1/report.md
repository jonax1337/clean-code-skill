I added `RefundOrder(orderId, amount)` to the order service, and the full suite passes (`java tools/RunTests.java`: 29 tests, 0 failed), including 9 new tests for refunds.

- **State rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status returns `INVALID_STATE`, and the order's status is never changed.
- **Cap:** the amount must not exceed `amountPaid − amountRefunded`, so all refunds together stay within what the customer actually paid. I used the amount paid rather than the order total, because the two can differ (a payment may be less than the total). A refund over the remaining balance returns `INVALID_INPUT`, and an order that was fully refunded rejects any further refund.
- **Recording:** a new `Order.recordRefund` adds the amount to `amountRefunded`.
- **Input checks:** the handler reuses the existing validation, so a blank order id or an amount that is zero, negative or has more than two decimals returns `INVALID_INPUT`. An unknown order returns `NOT_FOUND`.

The new files are `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. `Order.java` and `OrderServices.java` have small edits, and the handler is registered on the bus.

One thing to confirm with Support: an order that was cancelled can't be refunded, even if it was paid first. That follows the "only shipped or delivered" rule as written.