`RefundOrder(orderId, amount)` is now a command on the order service, and all 25 tests pass, including the new refund tests.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`. An unknown order fails with `NOT_FOUND`.
- **Amount rule:** the amount must be a valid positive money value, like the other commands. The total of all refunds can't exceed what the customer actually paid, which is `amountPaid` rather than `total`, since a voucher can make the paid amount lower. A refund over the remaining refundable amount fails with `INVALID_INPUT`.
- **Recording:** a successful refund adds to `amountRefunded` through a new `Order.refund(...)`, and the order's status stays as it is.

The new files are `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. I also registered the handler in `OrderServices.createBus` and added a row to the README's command table.

A refund of exactly the remaining refundable amount is allowed, so a fully refunded order stays `SHIPPED` or `DELIVERED`. Because the refundable amount reaches zero, any later refund on it is rejected.