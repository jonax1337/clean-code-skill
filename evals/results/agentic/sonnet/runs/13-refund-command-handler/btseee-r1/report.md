`RefundOrder(orderId, amount)` now works through the command bus. All 27 tests pass, including 7 new ones for refunds.

- **Status rule:** only `SHIPPED` or `DELIVERED` orders can be refunded. Any other status is rejected with `INVALID_STATE`.
- **Limit:** all refunds on an order together can't exceed `amountPaid`, not `total`. A customer who paid 60 on a 100 order can get back at most 60. Going over is rejected with `INVALID_INPUT`.
- **Recording:** each refund is added to `amountRefunded` on the order, and the status stays as it is.
- **Amount checks:** the amount must be positive with at most two decimals, and an unknown order returns `NOT_FOUND`. These checks are the same as for `PayOrder`.

The handler is `RefundOrderHandler`, registered in `OrderServices`. The recording method is `Order.recordRefund`, and I added a row for the command to the README table.

The README row for `RefundOrder` is wider than the other rows in that table, so its columns don't line up.

I haven't committed anything.