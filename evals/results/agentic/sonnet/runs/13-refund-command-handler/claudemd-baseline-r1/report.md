I added `RefundOrder(orderId, amount)` to the order service. I ran `java tools/RunTests.java` after the last edit, and all 29 tests passed, including 9 new ones for refunds.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status, cancelled included, fails with `INVALID_STATE`.
- **Cap:** the refunds already recorded plus the new one cannot exceed `amountPaid`, and I used what was paid rather than the order total. Partial refunds add up in `amountRefunded`. A refund that would go over the cap fails with `INVALID_INPUT` and records nothing.
- **Input and status:** the amount must be positive with at most two decimal places, and an unknown order gives `NOT_FOUND`. The order's status is left as it was.

The new code is `RefundOrder.java` and `RefundOrderHandler.java`, plus `Order.recordRefund`. The handler is registered in `OrderServices`, and I added a row for the command to the README table. The tests are in `RefundOrderHandlerTest`.

I haven't committed anything.