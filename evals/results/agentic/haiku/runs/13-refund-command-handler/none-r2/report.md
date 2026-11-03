`RefundOrder` is in place and the full suite passes: 28 tests, including 8 new ones for refunds. I haven't committed anything.

The command is `RefundOrder(orderId, amount)`, handled by `RefundOrderHandler` and registered in `OrderServices`. It applies Support's three rules:

- **Status:** only `SHIPPED` or `DELIVERED` orders can be refunded. Anything else fails with `INVALID_STATE`, and the status is never changed.
- **Cap:** the cap is `amountPaid`, not `total`, since the README notes these can differ. The check is `amount <= amountPaid - amountRefunded`, so repeated refunds can't exceed what was paid. A refund over the cap fails with `INVALID_INPUT`, the same code `PayOrder` uses for an amount over the total.
- **Recording:** the refund is added to `amountRefunded` through a new `Order.recordRefund(amount)` method, and the order is saved.

Amount validation reuses the existing `requireMoney` check, so zero, negative, or over-precise amounts are rejected.

Changes:
- `Order.java`: added `recordRefund`
- `RefundOrder.java` and `RefundOrderHandler.java`: new command and handler
- `OrderServices.java`: registered the handler
- `RefundOrderHandlerTest.java`: new tests for each rule
- `README.md`: added the command to the table and a short note on the rules

Two choices you may want to change:
- Refund amounts are checked against what was actually paid, so a refund on an order that was only partly paid can't exceed that partial amount.
- A refund over the cap returns `INVALID_INPUT` rather than a new error code. Say if Support wants a distinct code.