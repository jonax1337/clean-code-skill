I added the `RefundOrder(orderId, amount)` command, and all 28 tests pass, including 8 new ones for refunds.

- **Status rule:** Only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status fails with `INVALID_STATE`, and an unknown order fails with `NOT_FOUND`.
- **Amount rule:** The amount has to be positive with at most two decimal places, like `PayOrder`. The new refund plus `amountRefunded` must not exceed `amountPaid`. Otherwise it fails with `INVALID_INPUT` and nothing is saved.
- **Recording:** A successful refund adds to `amountRefunded` through a new `Order.recordRefund`, and the status stays as it was.

I capped refunds at `amountPaid`, not `total`. Your README says a voucher can make the amount paid lower than the total. Refunding up to the total would give back money the customer never paid.

The new code is in `RefundOrder.java`, `RefundOrderHandler.java` and `RefundOrderHandlerTest.java`. I also registered the handler in `OrderServices` and added a row to the README's command table. I haven't committed anything.