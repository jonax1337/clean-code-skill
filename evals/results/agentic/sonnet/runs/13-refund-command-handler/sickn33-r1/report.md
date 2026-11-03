I added the `RefundOrder(orderId, amount)` command, and all 27 tests pass, including 7 new ones for refunds.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`.
- **Refund cap:** the combined refunds can't exceed what the customer actually paid (`amountPaid`), not the order total. Paid can be lower than total, for example when a voucher covered part of the order. A refund that would go over fails with `INVALID_INPUT` and leaves the order unchanged.
- **Recording:** a successful refund is added to the order's `amountRefunded`, and the status stays as it was.
- **Input and errors:** `amount` must be positive with at most two decimal places, the same check `PayOrder` uses. An unknown order returns `NOT_FOUND`.

The new code is in `RefundOrder.java` and `RefundOrderHandler.java`, plus a small `Order.recordRefund` method. The handler is registered in `OrderServices.createBus`, I added a row to the README's command table, and the tests are in `RefundOrderHandlerTest.java`. I haven't committed anything.