I added `RefundOrder(orderId, amount)` with its own handler, `RefundOrderHandler`, and registered it in `OrderServices.createBus`. The full suite passes: 26 tests, including 6 new ones in `RefundOrderHandlerTest`.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Cap:** refunds are checked against what the customer actually paid (`amountPaid`), not the order total. They are not checked against the total because a voucher can leave the amount paid below it. Total refunds can never exceed `amountPaid`, and a refund above the remaining amount fails with `INVALID_INPUT`.
- **Recording:** the new `Order.recordRefund` adds the refund to `amountRefunded`, so partial refunds accumulate. The status is not changed.
- **Validation:** a blank order ID or a zero, negative or more-than-two-decimal amount fails with `INVALID_INPUT`, and an unknown order fails with `NOT_FOUND`. These are the same checks the other handlers use.
- **README:** I added a row for the new command to the command table.

A fully refunded order stays `SHIPPED` or `DELIVERED`, as you specified. I haven't committed anything.