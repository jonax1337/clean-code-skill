`RefundOrder(orderId, amount)` now works through the command bus, and all 27 tests pass, including 7 new ones for refunds.

- **State rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Anything else fails with `INVALID_STATE`.
- **Refund cap:** the total refunded can never exceed `amountPaid`. A customer who paid 80.00 on a 100.00 order can get back at most 80.00, not 100.00. Going over fails with `INVALID_INPUT`. The error message says how much is still refundable.
- **Recording:** each refund is added to `amountRefunded` on the order, so partial refunds accumulate. The status stays as it was.
- **Input checks:** the same checks as `PayOrder` apply. The order id can't be blank, and the amount must be positive with at most two decimals. An unknown order returns `NOT_FOUND`.

I did not run the crapper, dryer or mutator tools from the skill, and I haven't committed anything.

The new files are `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. I also added a `recordRefund` method to `Order` and registered the handler in `OrderServices`.